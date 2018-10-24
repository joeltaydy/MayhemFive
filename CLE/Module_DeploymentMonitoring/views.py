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
            response['access_key'] = decode(aws_credentials.access_key)
            response['secret_access_key'] = decode(aws_credentials.secret_access_key)

            # Compare AWS data with DB data; IF not in DB, add into DB
            image_list = aws_util.getAllImages(response['account_number'],response['access_key'],response['secret_access_key'])
            for image in image_list:
                if len(aws_credentials.imageDetails.all()) == 0:
                    image_detailsObj = utilities.addImageDetails(image)
                    aws_credentials.imageDetails.add(image_detailsObj)
                else:
                    querySet = aws_credentials.imageDetails.filter(imageId=image['Image_ID'])
                    if len(querySet) == 0:
                        image_detailsObj = utilities.addImageDetails(image)
                        aws_credentials.imageDetails.add(image_detailsObj)
                    else:
                        imageObj = querySet[0]
                        shared_acct_nums = [] if imageObj.sharedAccNum == None else imageObj.sharedAccNum.split('_')
                        registered_acct_nums = utilities.getRegisteredUsers(image['Launch_Permissions'])

                        # Add Image to AWS_Credentials
                        for acct in registered_acct_nums:
                            utilities.addImageToUser(imageObj,acct)

                        # Remove Image from AWS_Credentials
                        for acct in shared_acct_nums:
                            if acct not in registered_acct_nums:
                                utilities.removeImageFromAUser(imageObj,acct)

                        shared_acct_nums = '_'.join(registered_acct_nums)
                        imageObj.sharedAccNum = None if len(shared_acct_nums) == 0 else shared_acct_nums
                        imageObj.save()

            # Compare DB data with AWS data: IF not in AWS, delete from DB
            images = aws_credentials.imageDetails.all()
            for image_detailObj in images:
                db_image_id = image_detailObj.imageId
                match = False
                for image in image_list:
                    aws_image_id = image['Image_ID']

                    if db_image_id == aws_image_id:
                        match = True

                if not match:
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
def faculty_Setup_UpdateGitHubLinks(request,pk):
    dp = get_object_or_404(Deployment_Package, pk=pk)
    if request.method == 'POST':
        form = DeploymentForm(request.POST, instance=dp)
    else:
        form = DeploymentForm(instance=dp)
    return utilities.addGitHubLinkForm(request, form, 'dataforms/deploymentpackage/partial_dp_update.html')


# Deleting of github deployment package link from DB
# returns a JsonResponse
#
def faculty_Setup_DeleteGitHubLinks(request,pk):
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
            old_account_number = credentialsObj.account_number

            # Create NEW AWS_Credentials
            credentialsObj.account_number = account_number
            credentialsObj.access_key = encode(access_key)
            credentialsObj.secret_access_key = encode(secret_access_key)
            credentialsObj.save()

            facultyObj.awscredential = credentialsObj
            facultyObj.save()

            # Delete OLD AWS_Credentials and Images tied to it
            old_credentialsObj = AWS_Credentials.objects.get(account_number=old_account_number)

            imageObjs = old_credentialsObj.imageDetails.all()
            for imageObj in imageObjs:
                imageObj.delete()

            old_credentialsObj.delete()

        except:
            access_key = encode(access_key)
            secret_access_key = encode(secret_access_key)

            credentialsObj = AWS_Credentials.objects.create(
                account_number=account_number,
                access_key=access_key,
                secret_access_key=secret_access_key,
            )
            credentialsObj.save()

            facultyObj.awscredential = credentialsObj
            facultyObj.save()

        response['message'] = 'Successfully updated AWS Credentials'

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
    print("Ajax test section_number (faculty_Setup_GetAMI): " + response['section_number'])

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
    print("Ajax test section_number (faculty_Setup_GetAMIAccounts): " + section_number)

    image_id = requests.GET.get('image_id').strip()
    print("Ajax test image_id (faculty_Setup_GetAMIAccounts): " + image_id)

    try:
        response['shared_accounts_list'] = []
        response['nonshared_accounts_list'] = []

        imageObj = Image_Details.objects.get(imageId=image_id)
        shared_accounts = [] if imageObj.sharedAccNum == None else imageObj.sharedAccNum

        course_sectionList = requests.session['courseList_updated']
        section_teamList = utilities.getAllTeamDetails(course_sectionList)

        for details in section_teamList[section_number]:
            if details["account_number"] in shared_accounts:
                response['shared_accounts_list'].append(
                    {
                        'team_name':details["team_name"],
                        'account_number':details["account_number"]
                    }
                )
            else:
                response['nonshared_accounts_list'].append(
                    {
                        'team_name':details["team_name"],
                        'account_number':details["account_number"]
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

    choosen_account_list = requests.POST.getlist('account_numbers')
    image_id = requests.POST.get('image_id')
    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)

    try:
        # Get the access_key and secret_access_key from DB
        aws_credentials = facultyObj.awscredential
        access_key = decode(aws_credentials.access_key)
        secret_access_key = decode(aws_credentials.secret_access_key)

        client = aws_util.getClient(access_key,secret_access_key)

        if choosen_account_list != None:
            imageObj = Image_Details.objects.get(imageId=image_id)
            current_account_list = [] if imageObj.sharedAccNum == None else imageObj.sharedAccNum.split('_')

            # Step 1: ADD the account number to the image permission on AWS
            add_list = list(set(choosen_account_list)-set(current_account_list))
            if len(add_list) > 0:
                aws_util.addUserToImage(image_id,add_list,client=client)

            # Step 2: REMOVE the account number from the image permission on AWS
            remove_list = list(set(current_account_list)-set(choosen_account_list))
            if len(remove_list) > 0:
                aws_util.removeUserFromImage(image_id,remove_list,client=client)

            # Step 3: UPDATE image_details table with the new set of shared account numbers
            imageObj.sharedAccNum = choosen_account_list
            imageObj.save()

            # Step 4: ADD the image to AWS_Credentials (Student)
            for account_number in add_list:
                utilities.addImageToUser(imageObj,account_number)

            # Step 5 REMOVE the image from AWS_Credentials (Student)
            for account_number in remove_list:
                utilities.removeImageFromAUser(imageObj,account_number)

        response['message'] = 'Successfully shared Deployment Environment'

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

    if requests.method == "GET":
        section_num = requests.GET.get('section_number')
    else:
        section_num = requests.POST.get('section_number')

    response['server_status'] = []
    response['webapp_status'] = []
    response['event_log'] = []

    course_sectionList = requests.session['courseList_updated']
    response['first_section'] = course_sectionList['EMS201'][0]['section_number']
    response['course_sectionList'] = course_sectionList['EMS201']

    try:
        # Retrieve the team_number and account_number for each section
        course_sectionList = requests.session['courseList_updated']
        section_details = utilities.getAllTeamDetails(course_sectionList)[section_num]

        for details in section_details:
            response = utilities.getMonitoringStatus(details["account_number"],details["team_name"],response)
            # response['event_log'] = utilities.getEventLogs(details["account_number"],details["team_name"])

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Monitoring): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)


# Main function for ica deploy page for student.
# Will check if images has been shared by faculty
#
def student_Deploy_Base(requests):
    response = {'student_Deploy_Base' : 'active'}

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
        response['submittedAccNum'] = awsAccountNumber # Could be None or aws credentials object
    except:
        response['submittedAccNum'] = None

    try:
        awsAccountNumber =  class_studentObj.awscredential
        awsImageList = awsAccountNumber.imageDetails.all() # Could be None or aws image object Currently take first
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

    accountNum = requests.POST.get("accountNum")            #string of account number
    ipAddress = requests.POST.get("ipaddress")              #string of IP address

    if accountNum != "" :
        student_Deploy_AddAccount(requests)
    if ipAddress != "":
        try :
            student_Deploy_AddIP(requests)
            requests.session['newIP'] = ipAddress
            return student_Monitor_Base(requests)
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

    server_type = requests.POST.get("server_type")            #string of server_type; parent/slave
    ipAddress = requests.POST.get("ipaddress")              #string of IP address

    utilities.addAWSKeys(ipAddress,requests)
    utilities.addServerDetails(ipAddress,server_type,requests=requests)


# Retrieves student's server adn metrics
#
def student_Monitor_Base(requests):
    response = {"student_Monitor_Base" : "active"}

    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',{})

    response['server_ip'] = requests.GET.get('server_ip')

    try:
        response['server_status'] = []
        response['webapp_status'] = []
        response['webapp_metric'] = {}
        studentClassObj = utilities.getStudentClassObject(requests)

        AWS_Credentials = studentClassObj.awscredential
        team_number= studentClassObj.team_number
        account_number = AWS_Credentials.account_number

        if response['server_ip'] == None:
            if len(utilities.getAllServer(account_number)[0]) > 0:
                response['server_ip'] = utilities.getAllServer(account_number)[0]['server_ip']

        if response['server_ip'] != None:
            response = utilities.getMonitoringStatus(account_number,team_number,response)
            response = utilities.getMetric(response['server_ip'],response)

        tz = pytz.timezone('Asia/Singapore')
        response['last_updated']= str(datetime.datetime.now(tz=tz))[:19]

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Student Monitoring): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentMonitor.html", response)

    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentMonitor.html", response)

#--------------------------------------#
#--------------------------------------#
#--------------------------------------#

# Main function for deployment page on student.
# Will retrieve work products and render to http page
#
def student_Deploy_Standard_Base(requests,response=None):
    if response == None:
        response = {'student_Deploy_Base' : 'active'}

    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    classObj = utilities.getStudentClassObject(requests)
    credentialsObj = classObj.awscredential

    try:
        response['account_number'] = ''
        response['servers'] = []

        if credentialsObj != None:
            account_number = credentialsObj.account_number
            response['account_number'] = account_number
            response['servers'] = utilities.getAllServer(account_number)

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Student Deploy Standard): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeployStd.html", response)

    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeployStd.html", response)


# Adds account number into DB
#
def student_Deploy_Standard_AddAccount(requests):
    response = {'student_Deploy_Standard_AddAccount' : 'active'}

    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    new_account_number = None if requests.POST.get('new_account_number') == '' else requests.POST.get('new_account_number')
    old_account_number = None if requests.POST.get('old_account_number') == '' else requests.POST.get('old_account_number')

    try:
        if new_account_number == None:
            raise Exception('Please enter a valid account number')

        new_credentialsObj = AWS_Credentials.objects.create(account_number=new_account_number)
        new_credentialsObj.save()

        if old_account_number != None:
            querySet = Class.objects.filter(awscredential=old_account_number)
            for studentClassObj in querySet:
                studentClassObj.awscredential = new_credentialsObj
                studentClassObj.save()

            serverObjs = Server_Details.objects.filter(account_number=old_account_number)
            for serverObj in serverObjs:
                serverObj.delete()

            old_credentialsObj = AWS_Credentials.objects.get(account_number=old_account_number)
            old_credentialsObj.delete()
        else:
            team_members = utilities.getTeamMembersClassQuerySet(requests)
            print(team_members)
            for team_member in team_members:
                team_member.awscredential = new_credentialsObj
                team_member.save()

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during validating of new account number (Student Deploy Standard): ' + str(e.args[0])
        return student_Deploy_Standard_Base(requests,response)

    return student_Deploy_Standard_Base(requests,response)


# Retrieval of github deployment package link from DB
#
def student_Deploy_Standard_GetIPs(requests):
    classObj = utilities.getStudentClassObject(requests)
    credentialsObj = classObj.awscredential
    servers = []

    if credentialsObj != None:
        servers = utilities.getAllServer(credentialsObj.account_number)

    return render(requests, 'dataforms/serverdetails/server_list.html', {'servers': servers})


# Adding of server to DB
# returns a JsonResponse
#
def student_Deploy_Standard_AddIPs(requests):
    if requests.method == 'POST':
        studentClassObj = utilities.getStudentClassObject(requests)
        credentialsObj = studentClassObj.awscredential

        if credentialsObj.access_key == None and credentialsObj.secret_access_key == None:
            utilities.addAWSKeys(requests.POST.get('IP_address'),requests)

        form = ServerForm_Add(requests.POST)
    else:
        form = ServerForm_Add()

    response = utilities.addServerDetailsForm(requests, form, 'dataforms/serverdetails/partial_server_create.html')

    if requests.method == 'POST':
        utilities.initiateStartServerTime(requests.POST.get('IP_address'))

    return response


# Updating of server in DB
# returns a JsonResponse
#
def student_Deploy_Standard_UpdateIPs(requests,pk):
    server = get_object_or_404(Server_Details, pk=pk)

    if requests.method == 'POST':
        form = ServerForm_Update(requests.POST, instance=server)
    else:
        form = ServerForm_Update(instance=server)

    return utilities.addServerDetailsForm(requests, form, 'dataforms/serverdetails/partial_server_update.html')


# Deleting of server from DB
# returns a JsonResponse
#
def student_Deploy_Standard_DeleteIPs(requests,pk):
    classObj = utilities.getStudentClassObject(requests)
    credentialsObj = classObj.awscredential
    server = get_object_or_404(Server_Details, pk=pk)
    data = dict()

    if requests.method == 'POST':
        server.delete()
        data['form_is_valid'] = True
        servers = utilities.getAllServer(credentialsObj.account_number)
        data['html_server_list'] = render_to_string('dataforms/serverdetails/partial_server_list.html', {
            'servers': servers
        })
    else:
        context = {'server': server}
        data['html_form'] = render_to_string('dataforms/serverdetails/partial_server_delete.html',
            context,
            request=requests,
        )

    return JsonResponse(data)
