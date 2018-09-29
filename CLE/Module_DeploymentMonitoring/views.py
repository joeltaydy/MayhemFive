import traceback
from django.shortcuts import render
from django.http import HttpResponse
from Module_DeploymentMonitoring.models import *
from Module_TeamManagement.models import *
from django.db.models import Count
from Module_DeploymentMonitoring.src import *

# Required for verification
from Module_Account.src import processLogin
from django.contrib.auth import logout
import requests as req


'''
Main function for setup page on faculty.
Will retrieve work products and render to http page
'''
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
            image_list = utilities.getAllImages(account_number,access_key,secret_access_key)
            for image_id,image_name in image_list.items():
                try:
                    Image_Details.objects.get(imageId=image_id)
                except:
                    image_detailsObj = Image_Details.objects.create(
                        imageId=image_id,
                        imageName=image_name,
                    )
                    image_detailsObj.save()

            # Retrieve Shared Account Numbers from Image_Details (DB)
            # IF does not exists in DB, DELETE
            # ELSE, populate section_imageList with the right details
            querySet = Image_Details.objects.all()
            for image_details in querySet:
                id = image_details.imageId
                name = image_details.imageName

                try:
                    image_list[id] # RED HAIR-RING ;D

                    for section_number,section_details in section_list.items():
                        section_imageList[section_number] = {'Image_IDs':[]}
                        sharedList = []
                        nonsharedList = []

                        for account_number,team_name in section_details.items():
                            if account_number not in image_details.sharedAccNum:
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
                    image_details.delete()

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


'''
Retrieval and storing of github deployment package link from instructor
returns to setup page
'''
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


'''
Retrieval and storing of AWS keys from instructor
returns to setup page
'''
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


'''
Retrieval and storing of AMI length from instructor
returns to setup page
'''
def faculty_Setup_ShareAMI(requests):
    response = {"faculty_Setup_ShareAMI" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    try:
        pass

    except:
        traceback.print_exc()
        response['message'] = 'Error in Share AMI form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


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

    accountNum = requests.POST.get("AWS_account_number") #string of account number
    utilities.addAWSCredentials(accountNum, requests) #creates an incomplete account object

    return HttpResponse('')


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
