import traceback
from django.shortcuts import render
from django.http import HttpResponse
from Module_DeploymentMonitoring.models import *
from Module_TeamManagement.models import *
from Module_DeploymentMonitoring.src import utilities

# Required for verification
from Module_Account.src import processLogin
from django.contrib.auth import logout

'''
Main function for setup page on faculty.
Will retrieve work products and render to http page
'''
def faculty_Setup_Base(requests):
    response = {"ITOpsLabSetup" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)

    try:
        # Retrieve GitHub link from Deployment_Package
        deployment_packageObjs = Deployment_Package.objects.all()
        deployment_packageList = []

        if len(deployment_packageObjs) > 0:
            for deployment_packageObj in deployment_packageObjs:
                deployment_packageList.append(
                    {
                        deployment_packageObj.deploymentid:deployment_packageObj.gitlink
                    }
                )

        # Retrieve Access_Key and Secret_Access_Key from AWS_Credentials
        aws_credentials = facultyObj.awscredential
        account_number = ''
        access_key = ''
        secret_access_key = ''
        image_list_w_account_numbers = []

        if aws_credentials != None:
            account_number = aws_credentials.account_number
            access_key = aws_credentials.access_key
            secret_access_key = aws_credentials.secret_access_key

            # Retreive image_id and image_name from AWS using Boto3
            image_list = utilities.getAllImages(account_number,access_key,secret_access_key)

            # Retrieve Shared Account Number from Image_Details
            for image_id,image_name in image_list.items():
                try:
                    image_detailObj = Image_Details.objects.get(imageId=image_id)
                    account_numbers = image_detailObj.account_numbers
                    
                except:
                    pass

        response['deployment_packages'] = deployment_packageList
        response['account_number'] = account_number
        response['access_key'] = access_key
        response['secret_access_key'] = secret_access_key
        response['images'] = image_list_w_account_numbers

    except:
        traceback.print_exc()
        # Put error messages here

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)


'''
Retrieval and storing of github deployment package link from instructor
returns to setup page
'''
def faculty_Setup_GetGitHub(requests):

    return faculty_Setup_Base(requests)


'''
Retrieval and storing of AWS keys from instructor
returns to setup page
'''
def faculty_Setup_GetAWSKeys(requests):

    return faculty_Setup_Base(requests)


'''
Retrieval and storing of AMI length from instructor
returns to setup page
'''
def faculty_Setup_ShareAMI(requests):

    return faculty_Setup_Base(requests)


def student_Deploy_Base(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
    except:

        logout(requests)
        return render(requests,'Module_Account/login.html',response)
    
    student_email = requests.user.email
    courseList = requests.session['courseList_updated']
    for crse in courseList:
        if crse.course_title == "EMS201":
            coursesec = crse
    class_studentObj = Class.objects.get(student= student_email).get(course_section=coursesec )

    awsAccountNumber =  class_studentObj.awscredential
    response['awsAccNum'] = awsAccountNumber #Could be None or aws credentials object
    try:
        awsImage = awsAccountNumber.imageDetails #Could be None or aws image object
        response['awsImage'] = awsImage
    except:
        response['awsImage'] = None

    response["studentDeployBase"] = "active"

    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)

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

    
    student_email = requests.user.email
    courseList = requests.session['courseList_updated']
    for crse in courseList:
        if crse.course_title == "EMS201":
            coursesec = crse
    class_studentObj = Class.objects.get(student= student_email).get(course_section=coursesec)

    accountNum = requests.POST.get("AWS_account_number") #string of account number
    utilities.createAccount(accountNum, class_studentObj) #creates an incomplete account object


    return HttpResponse('')


def student_Deploy_GetIP(requests):

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
