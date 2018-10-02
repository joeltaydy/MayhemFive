import traceback
import requests as req
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from Module_DeploymentMonitoring.models import *
from Module_TeamManagement.models import *
from Module_DeploymentMonitoring.src import *
from Module_Account.src import processLogin
from django.contrib.auth import logout

from django.http import JsonResponse
from django.template.loader import render_to_string
from Module_DeploymentMonitoring.forms import *




# Main function for setup page on faculty.
# Will retrieve work products and render to http page
#
def faculty_Setup_Base(requests,response=None):
    response = {"faculty_Setup_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)

    try:
        deployment_packageList = {}
        account_number = ''
        access_key = ''
        secret_access_key = ''
        section_imageList = {}

        # Retrieve GitHub link from Deployment_Package
        deployment_packageObjs = Deployment_Package.objects.all()

        if len(deployment_packageObjs) > 0:
            for deployment_packageObj in deployment_packageObjs:
                deployment_packageList.update(
                    {
                        deployment_packageObj.deploymentid:deployment_packageObj.gitlink
                    }
                )

        # Retrieve Access_Key and Secret_Access_Key from AWS_Credentials
        aws_credentials = facultyObj.awscredential

        if aws_credentials != None:
            account_number = aws_credentials.account_number
            access_key = aws_credentials.access_key
            secret_access_key = aws_credentials.secret_access_key

            # Retrieve the team_number and account_number for each section
            section_list = utilities.getAllTeamDetails()

            # Retreive image_id and image_name from AWS using Boto3
            # IF exists in DB, PASS
            # ELSE, ADD into DB
            image_list = aws_util.getAllImages(account_number,access_key,secret_access_key)
            images = aws_credentials.imageDetails.all()
            for image_id,image_name in image_list.items():
                isIn = False
                for image_detailObj in images:
                    if image_detailObj.imageId == image_id:
                        isIn = True

                if not isIn:
                    image_detailsObj = Image_Details.objects.create(
                        imageId=image_id,
                        imageName=image_name,
                    )
                    image_detailsObj.save()
                    aws_credentials.imageDetails.add(image_detailsObj)

            # Retrieve Shared Account Numbers from Image_Details (DB)
            # IF does not exists in DB, DELETE
            # ELSE, populate section_imageList with the right details
            images = aws_credentials.imageDetails.all()
            for image_detailObj in images:
                id = image_detailObj.imageId
                name = image_detailObj.imageName

                try:
                    image_list[id] # Just to check if it DB info tallies with AWS

                    for section_number,section_details in section_list.items():
                        section_imageList[section_number] = {'Image_IDs':[]}
                        sharedList = []
                        nonsharedList = []

                        for account_number,team_name in section_details.items():
                            if account_number not in image_detailObj.sharedAccNum:
                                nonsharedList.append(
                                    {
                                        'account_number':account_number,
                                        'team_name':team_name,
                                    }
                                )
                            else:
                                sharedList.append(
                                    {
                                        'account_number':account_number,
                                        'team_name':team_name,
                                    }
                                )

                        section_imageList[section_number]['Image_IDs'].append(
                            {
                                'image_id':id,
                                'image_name':name,
                                'shared_account_number':sharedList,
                                'non_shared_account_number':nonsharedList
                            }
                        )
                except:
                    image_detailObj.delete()

    except Exception as e:
        traceback.print_exc()
        response['message'] = 'Error during retrieval of information: ' + e.args[0]
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)

    finally:
        response['deployment_packages'] = deployment_packageList
        response['account_number'] = account_number
        response['access_key'] = access_key
        response['secret_access_key'] = secret_access_key
        response['section_imageList'] = section_imageList

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)


# Retrieval and storing of github deployment package link from instructor
# returns to faculty_Setup_Base
#
def faculty_Setup_GetGitHub(requests):
    response = {"faculty_Setup_GetGitHub" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    package_id = requests.GET.get('package_id')
    github_link = requests.GET.get('github_link')

    try:
        if package_id == None:
            raise Exception('Please input a valid package name')

        if github_link == None:
            raise Exception('Please input a valid GitHub link')

        # Save/Update GitHub link to Deployment_Package
        try:
            deployment_packageObj = Deployment_Package.objects.get(deploymentid=package_id)
            deployment_packageObj.gitlink = github_link
            deployment_packageObj.save()
        except:
            Deployment_Package.objects.create(
                deploymentid=package_id,
                gitlink=github_link,
            )
            Deployment_Package.save()

    except Exception as e:
        traceback.print_exc()
        response['message'] = 'Error in Deployment Package form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


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

    account_number = requests.GET.get('account_number')
    access_key = requests.GET.get('access_key')
    secret_access_key = requests.GET.get('secret_access_key')

    try:
        if account_number == None:
            raise Exception('Please input an account_number')

        # Save/Update Account_Number, Access_Key and Secret_Access_Key to AWS_Credentials
        try:
            if access_key == None and secret_access_key == None:
                raise Exception('Please input an access_key and/or secret_access_key')

            credentialsObj = AWS_Credentials.objects.get(account_number=account_number)

            if access_key != None:
                credentialsObj.access_key = access_key

            if secret_access_key != None:
                credentialsObj.secret_access_key = secret_access_key

            credentialsObj.save()
        except:
            if access_key == None:
                raise Exception('Please input an access_key')

            if secret_access_key == None:
                raise Exception('Please input a secret_access_key')

            credentialsObj = AWS_Credentials.objects.create(
                account_number=account_number,
                access_key=access_key,
                secret_access_key=secret_access_key,
            )
            credentialsObj.save()

    except:
        traceback.print_exc()
        response['message'] = 'Error in AWS Information form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


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

    account_numbers = requests.GET.get('account_numbers')
    image_id = requests.GET.get('image_id')
    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)

    try:
        # Get the access_key and secret_access_key from DB
        aws_credentials = facultyObj.awscredential
        access_keys = aws_credentials.access_keys
        secret_access_keys = aws_credentials.secret_access_keys

        client = aws_util.getEC2Client(access_keys,secret_access_keys)

        for account_number in account_numbers:
            # Add the account number to the image permission on AWS
            aws_util.addUserToImage(client,image_id,account_number)

            # Add the account number to DB side
            image_detailObj = aws_credentials.imageDetails.filter(imageId=image_id)[0]
            account_numbers = image_detailObj.sharedAccNum

            if account_numbers == None:
                image_detailObj.sharedAccNum = account_number
            else:
                image_detailObj.sharedAccNum = account_numbers + '_' + account_number

            image_detailObj.save()

    except:
        traceback.print_exc()
        response['message'] = 'Error in Share AMI form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


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

    awsAccountNumber =  class_studentObj.awscredential
    response['awsAccNum'] = awsAccountNumber #Could be None or aws credentials object
    try:
        awsImage = awsAccountNumber.imageDetails #Could be None or aws image object
        response['awsImage'] = awsImage
    except:
        response['awsImage'] = None

    response["studentDeployBase"] = "active"

    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)


# Storing of student user account number in database
#
def student_Deploy_GetAccount(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            response['message'] = "Wrong entry to form"
            return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    accountNum = requests.POST.get("AWS_account_number") #string of account number
    utilities.addAWSCredentials(accountNum, requests) #creates an incomplete account object

    return HttpResponse('')


# Storing and validating of student user IP address
#
def student_Deploy_GetIP(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            response['message'] = "Wrong entry to form"
            return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    ipAddress = requests.POST.get("ip") #string of IP address
    utilities.addAWSKeys(ipAddress,requests)
    utilities.addServerDetails(ipAddress,requests)

    return HttpResponse('')


def ITOpsLabMonitor(requests):
    response = {"ITOpsLabMonitor" : "active"}
    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)

def ITOpsLabEvent(requests):
    response = {"ITOpsLabEvent" : "active"}
    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)

def ITOpsLabStudentDeploy(requests):
    response = {"ITOpsLabStudentDeploy" : "active"}
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)

def ITOpsLabStudentMonitor(requests):
    response = {"ITOpsLabStudentMonitor" : "active"}
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


#deployment package forms
def deployment_package_list(request):
    dps = Deployment_Package.objects.all()
    return render(request, 'dataforms/deploymentpackage/dp_list.html', {'dps': dps})


def save_dp_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            dps = Deployment_Package.objects.all()
            data['html_dp_list'] = render_to_string('dataforms/deploymentpackage/partial_dp_list.html', {
                'dps': dps
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def dp_create(request):
    if request.method == 'POST':
        form = DeploymentForm(request.POST)
    else:
        form = DeploymentForm()
    return save_dp_form(request, form, 'dataforms/deploymentpackage/partial_dp_create.html')


def dp_update(request, pk):
    dp = get_object_or_404(Deployment_Package, pk=pk)
    if request.method == 'POST':
        form = DeploymentForm(request.POST, instance=dp)
    else:
        form = DeploymentForm(instance=dp)
    return save_dp_form(request, form, 'dataforms/deploymentpackage/partial_dp_update.html')


def dp_delete(request, pk):
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
#end of deployment package forms
