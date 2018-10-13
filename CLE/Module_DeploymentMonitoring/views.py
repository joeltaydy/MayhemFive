import json
import pytz
import datetime
import traceback
import requests as req
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from Module_DeploymentMonitoring.models import *
from Module_TeamManagement.models import *
from Module_DeploymentMonitoring.src import utilities,aws_util
from Module_Account.src import processLogin
from django.contrib.auth import logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from Module_DeploymentMonitoring.forms import *
from Module_TeamManagement.src.utilities import encode,decode

# from django.http import QueryDict

# Main function for setup page on faculty.
# Will retrieve work products and render to http page
#
def faculty_Setup_Base(requests,response=None):
    if response == None:
        response = {"faculty_Setup_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)
    response['first_section'] = requests.session['courseList_updated']['EMS201'][0]['section_number']

    try:
        response['deployment_packages'] = []
        response['account_number'] = ''
        response['access_key'] = ''
        response['secret_access_key'] = ''
        response['section_numbers'] = []

        # Retrieve Setions that are under EMS201 for faculty
        ems_course_sectionList = requests.session['courseList_updated']['EMS201']
        for course_section in ems_course_sectionList:
            response['section_numbers'].append(course_section['section_number'])

        # Retrieve GitHub link from Deployment_Package
        deployment_packageObjs = Deployment_Package.objects.all()

        if len(deployment_packageObjs) > 0:
            for deployment_packageObj in deployment_packageObjs:
                response['deployment_packages'].append(
                    {
                        'package_name':deployment_packageObj.deploymentid,
                        'package_link':deployment_packageObj.gitlink
                    }
                )

        # Retrieve Access_Key and Secret_Access_Key from AWS_Credentials
        aws_credentials = facultyObj.awscredential

        if aws_credentials != None:
            response['account_number']  = aws_credentials.account_number
            response['access_key'] = aws_credentials.access_key
            response['secret_access_key'] = aws_credentials.secret_access_key

            # Compare AWS data with DB data; IF not in DB, add into DB
            image_list = aws_util.getAllImages(response['account_number'],response['access_key'],response['secret_access_key'])
            for image_id,image_name in image_list.items():
                if len(aws_credentials.imageDetails.all()) == 0:
                    image_detailsObj = utilities.addImageDetials(image_id,image_name)
                    aws_credentials.imageDetails.add(image_detailsObj)
                else:
                    querySet = aws_credentials.imageDetails.filter(imageId=image_id)
                    if len(querySet) == 0:
                        image_detailsObj = utilities.addImageDetials(image_id,image_name)
                        aws_credentials.imageDetails.add(image_detailsObj)
                    else:
                        pass

            # Compare DB data with AWS data: IF not in AWS, delete from DB
            images = aws_credentials.imageDetails.all()
            for image_detailObj in images:
                try:
                    image_list[image_detailObj.imageId]
                except:
                    image_detailObj.delete()

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Setup): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)


# Retrieval of github deployment package link from DB
#
def faculty_Setup_GetGitHubLinks(request):
    dps = Deployment_Package.objects.all()
    return render(request, 'dataforms/deploymentpackage/dp_list.html', {'dps': dps})


# Adding of github deployment package link to DB
# returns a JsonResponse
#
def faculty_Setup_AddGitHubLinks(request):
    if request.method == 'POST':
        form = DeploymentForm(request.POST)
    else:
        form = DeploymentForm()
    return utilities.addGitHubLinkForm(request, form, 'dataforms/deploymentpackage/partial_dp_create.html')


# Updating of github deployment package link to DB
# returns a JsonResponse
#
def faculty_Setup_UpdateGitHubLinks(request, pk):
    dp = get_object_or_404(Deployment_Package, pk=pk)
    if request.method == 'POST':
        form = DeploymentForm(request.POST, instance=dp)
    else:
        form = DeploymentForm(instance=dp)
    return utilities.addGitHubLinkForm(request, form, 'dataforms/deploymentpackage/partial_dp_update.html')


# Deleting of github deployment package link from DB
# returns a JsonResponse
#
def faculty_Setup_DeleteGitHubLinks(request, pk):
    dp = get_object_or_404(Deployment_Package, pk=pk)
    data = dict()
    if request.method == 'POST':
        dp.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        dps = Deployment_Package.objects.all()
        data['html_dp_list'] = render_to_string('dataforms/deploymentpackage/partial_dp_list.html', {
            'dps': dps
        })
    else:
        context = {'dp': dp}
        data['html_form'] = render_to_string('dataforms/deploymentpackage/partial_dp_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)


# Retrieval and storing of AWS keys from instructor
# returns to faculty_Setup_Base
#
def faculty_Setup_GetAWSKeys(requests):
    response = {"faculty_Setup_GetAWSKeys" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    account_number = requests.POST.get('account_number')
    access_key = requests.POST.get('access_key')
    secret_access_key = requests.POST.get('secret_access_key')

    try:
        if account_number == None or access_key == None or secret_access_key == None:
            raise Exception('Please input an account_number, access_key and secret_access_key')

        faculty_email = requests.user.email
        facultyObj = Faculty.objects.get(email=faculty_email)

        # Validate if account_number is a valid account_number
        valid = aws_util.validateAccountNumber(account_number,access_key,secret_access_key)
        if not valid:
            raise Exception("Invalid parameters. Please specify a valid account number.")

        # try:UPDATE, except:SAVE Account_Number, Access_Key and Secret_Access_Key to AWS_Credentials
        try:
            credentialsObj = facultyObj.awscredential
            credentialsObj.account_number = account_number
            credentialsObj.access_key = access_key
            credentialsObj.secret_access_key = secret_access_key
            credentialsObj.save()

            facultyObj.awscredential = credentialsObj
            facultyObj.save()

        except:
            credentialsObj = AWS_Credentials.objects.create(
                account_number=account_number,
                access_key=access_key,
                secret_access_key=secret_access_key,
            )
            credentialsObj.save()

            facultyObj.awscredential = credentialsObj
            facultyObj.save()

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error in AWS Information form: ' + str(e.args[0])
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


# Reteival of all the Images under the faculty account
#
def faculty_Setup_GetAMI(requests):
    response = {"facutly_Setup_GetAMI" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    response['section_number'] = requests.GET.get('section_number').strip()
    print("Ajax test section_numberList: " + response['section_number'])

    try:
        response['images'] = []

        faculty_email = requests.user.email
        facultyObj = Faculty.objects.get(email=faculty_email)
        aws_credentialsObj = facultyObj.awscredential

        images_detailObjs = aws_credentialsObj.imageDetails.all()
        for image in images_detailObjs:
            response['images'].append(
                {
                    'image_name':image.imageName,
                    'image_id':image.imageId
                }
            )

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error in Get AMI form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return HttpResponse(json.dumps(response), content_type='application/json')


# Reteival of shared and non-shared account numbers for specific section and image
#
def faculty_Setup_GetAMIAccounts(requests):
    response = {"faculty_Setup_GetAMIAccounts" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    section_number = requests.GET.get('section_number').strip()
    print("Ajax test section_number: " + section_number)

    image_id = requests.GET.get('image_id').strip()
    print("Ajax test image_id: " + image_id)

    try:
        response['shared_accounts_list'] = []
        response['nonshared_accounts_list'] = []

        imageObj = Image_Details.objects.get(imageId=image_id)
        shared_accounts = [] if imageObj.sharedAccNum == None else imageObj.sharedAccNum

        course_sectionList = requests.session['courseList_updated']
        section_teamList = utilities.getAllTeamDetails(course_sectionList)

        for team_name,account_number in section_teamList[section_number].items():
            if account_number in shared_accounts:
                response['shared_accounts_list'].append(
                    {
                        'team_name':team_name,
                        'account_number':account_number
                    }
                )
            else:
                response['nonshared_accounts_list'].append(
                    {
                        'team_name':team_name,
                        'account_number':account_number
                    }
                )

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error in Get AMI-Accounts form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return HttpResponse(json.dumps(response), content_type='application/json')


# Retrieval and storing of AMI length from instructor
# returns to faculty_Setup_Base
#
def faculty_Setup_ShareAMI(requests):
    response = {"faculty_Setup_ShareAMI" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    account_numbers = requests.POST.getlist('account_numbers')
    image_id = requests.POST.get('image_id')
    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)

    try:
        # Get the access_key and secret_access_key from DB
        aws_credentials = facultyObj.awscredential
        access_key = aws_credentials.access_key
        secret_access_key = aws_credentials.secret_access_key

        # Add the account number to the image permission on AWS
        client = aws_util.getClient(access_key,secret_access_key)

        if account_numbers != None:
            if len(account_numbers) > 0:
                aws_util.addUserToImage(image_id,account_numbers,client=client)

                for account_number in account_numbers:
                    # Add the account number to DB side
                    image_detailObj = aws_credentials.imageDetails.filter(imageId=image_id)[0]
                    shared_account_numbers = image_detailObj.sharedAccNum

                    if shared_account_numbers == None:
                        shared_account_numbers = account_number
                    else:
                        shared_account_numbers = shared_account_numbers.split('_')
                        if account_number not in shared_account_numbers:
                            shared_account_numbers = '-'.join(shared_account_numbers) + '_' + account_number
                        else:
                            shared_account_numbers = '-'.join(shared_account_numbers)

                    image_detailObj.sharedAccNum = shared_account_numbers
                    image_detailObj.save()

                    # Add the image to the student AWS_Credentials using their account number
                    stu_credentials = AWS_Credentials.objects.get(account_number=account_number)
                    stu_credentials.imageDetails.add(image_detailObj)
                    stu_credentials.save()

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error in Share AMI form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


# Main function for monitor page on faculty.
#
def faculty_Monitor_Base(requests):
    response = {"faculty_Monitor_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    section_num = requests.GET.get('section_number')
    response['server_status'] = {}
    response['webapp_status'] = {}

    course_sectionList = requests.session['courseList_updated']
    response['first_section'] = course_sectionList['EMS201'][0]['section_number']
    response['course_sectionList'] = course_sectionList['EMS201']

    try:
        # Retrieve the team_number and account_number for each section
        course_sectionList = requests.session['courseList_updated']
        section_details = utilities.getAllTeamDetails(course_sectionList)[section_num]

        for team_number,account_number in section_details.items():
            response = utilities.getMonitoringStatus(account_number,team_number,response)

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Monitoring): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)


# Main function for event configuration page on faculty.
#
def faculty_Event_Base(requests):
    response = {"faculty_Event_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)
    course_sectionList = requests.session['courseList_updated']

    response['course_sectionList'] = course_sectionList['EMS201']
    response['first_section'] = course_sectionList['EMS201'][0]['section_number']

    # Second round retrieval
    section_numberList = requests.POST.getlist('section_number')
    event_type = requests.POST.get('event_type')
    datetime = requests.POST.get('datetime')

    try:
        team_details = utilities.getAllTeamDetails(course_sectionList)
        for section_number in section_numberList:
            for team_name,account_number in team_details[section_number].items():
                querySet_serverList = Server_Details.objects.filter(account_number=account_number)
                for server in querySet_serverList:
                    server_ip = server.IP_address
                    server_id = server.instanceid

                    event_response = utilities.runEvent(server_ip,server_id,event_type)
                    print(event_response)
                    # Not sure what to do with the event_response yet

                    return faculty_Monitor_Base(requests)

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Event Configuration): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)


# Main function for deploy page on student.
# Will check if images has been shared by faculty
#
def student_Deploy_Base(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
    except:

        logout(requests)
        return render(requests,'Module_Account/login.html',response)
    coursesec = ""
    student_email = requests.user.email
    courseList = requests.session['courseList_updated']
    for course_title, crse in courseList.items():
        if course_title == "EMS201":
            coursesec = crse['id']
    class_studentObj = Class.objects.filter(student= student_email).get(course_section=coursesec )

    try:
        awsAccountNumber =  class_studentObj.awscredential
        response['submittedAccNum'] = awsAccountNumber #Could be None or aws credentials object
    except:
        response['submittedAccNum'] = None
    try:
        awsAccountNumber =  class_studentObj.awscredential
        awsImageList = awsAccountNumber.imageDetails.all() #Could be None or aws image object Currently take first
        accountNumber = awsAccountNumber.account_number
        consistent = False
        for image in awsImageList:
            if accountNumber in image.sharedAccNum:
                response['awsImage'] = image
                response['approvalStatus']= True
                consistent = True
                break
        if consistent != True:
            response['awsImage'] = None
            response['approvalStatus']= False

    except:
        response['awsImage'] = None
        response['approvalStatus']= False

    response["studentDeployBase"] = "active"
    print(response)
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)


# Processes Form
#
def student_Deploy_Upload(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            student_Deploy_Base(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)
    accountNum = requests.POST.get("accountNum") #string of account number
    ipAddress = requests.POST.get("ipaddress") #string of IP address
    if accountNum != "" :
        student_Deploy_AddAccount(requests)
    if ipAddress != "":
        try :
            student_Deploy_AddIP(requests)
            return ITOpsLabStudentMonitor(requests)
        except:
            traceback.print_exc()
    return student_Deploy_Base(requests)


# Storing of student user account number in database
#
def student_Deploy_AddAccount(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            response['error_message'] = "Wrong entry to form"
            return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    accountNum = requests.POST.get("accountNum") #string of account number
    utilities.addAWSCredentials(accountNum, requests) #creates an incomplete account object


# Storing and validating of student user IP address
#
def student_Deploy_AddIP(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            response['error_message'] = "Wrong entry to form"
            return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    ipAddress = requests.POST.get("ipaddress") #string of IP address
    print(ipAddress)
    utilities.addAWSKeys(ipAddress,requests)
    utilities.addServerDetails(ipAddress,requests)


def ITOpsLabStudentDeploy(requests):
    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',{})

    response = {"ITOpsLabStudentDeploy" : "active"}
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)


def ITOpsLabStudentMonitor(requests):

    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',{})

    response = {"ITOpsLabStudentDeploy" : "active"}
    try:
        response['server_status'] = {}
        response['webapp_status'] = {}
        response['webapp_metric'] = {}
        studentClassObj = utilities.getStudentClassObject(requests)
        AWS_Credentials = studentClassObj.awscredential
        team_number= studentClassObj.team_number
        account_number = AWS_Credentials.account_number
        response = utilities.getMonitoringStatus(account_number,team_number,response)
        response = utilities.getMetric(account_number,response)
        tz = pytz.timezone('Asia/Singapore')
        response["last_updated"]= str(datetime.datetime.now(tz=tz))[:19]
    except:
        pass
    print(response)
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentMonitor.html", response)






#test forms
def server_list(request):
    servers = Server_Details.objects.all()
    return render(request, 'Module_TeamManagement/Datatables/server_list.html', {'servers': servers})


def save_server_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            servers = Server_Details.objects.all()
            data['html_server_list'] = render_to_string('Module_TeamManagement/Datatables/partial_server_list.html', {
                'servers': servers
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def server_create(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
    else:
        form = ServerForm()
    return save_server_form(request, form, 'Module_TeamManagement/Datatables/partial_server_create.html')


def server_update(request, pk):
    server = get_object_or_404(Server_Details, pk=pk)
    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
    else:
        form = ServerForm(instance=server)
    return save_server_form(request, form, 'Module_TeamManagement/Datatables/partial_server_update.html')


def server_delete(request, pk):
    server = get_object_or_404(Server_Details, pk=pk)
    data = dict()
    if request.method == 'POST':
        server.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        servers = Server_Details.objects.all()
        data['html_server_list'] = render_to_string('Module_TeamManagement/Datatables/partial_server_list.html', {
            'servers': servers
        })
    else:
        context = {'server': server}
        data['html_form'] = render_to_string('Module_TeamManagement/Datatables/partial_server_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)
#end of test forms
