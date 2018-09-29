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
    facultyObj = Faculty.objects.get(email=requests.user.email)

    try:
        # Retrieve GitHub link from Deployment_Package
        deployment_packageObjs = Deployment_Package.objects.all()
        deployment_packageList = {}

        if len(deployment_packageObjs) > 0:
            for deployment_packageObj in deployment_packageObjs:
                deployment_packageList.update(
                    {
                        deployment_packageObj.deploymentid:deployment_packageObj.gitlink
                    }
                )

        # Retrieve Access_Key and Secret_Access_Key from AWS_Credentials
        aws_credentials = facultyObj.awscredential
        account_number = ''
        access_key = ''
        secret_access_key = ''
        section_imageList = {}

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
                        section_imageList[section_number] = {'Image_IDs'[]}
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
                                'shared_account_number':sharedList
                                'non_shared_account_number':nonsharedList
                            }
                        )
                except:
                    image_details.delete()

        response['deployment_packages'] = deployment_packageList
        response['account_number'] = account_number
        response['access_key'] = access_key
        response['secret_access_key'] = secret_access_key
        response['image_list'] = image_list
        response['section_imageList'] = section_imageList

    except:
        traceback.print_exc()
        # TO-DO: Put error messages here

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)


'''
Retrieval and storing of github deployment package link from instructor
returns to setup page
'''
def faculty_Setup_GetGitHub(requests):
    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    package_id = requests.GET.get('package_id')
    github_link = requests.GET.get('github_link')

    try:
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

    except:
        traceback.print_exc()
        # TO-DO: Put error messages here

    return faculty_Setup_Base(requests)


'''
Retrieval and storing of AWS keys from instructor
returns to setup page
'''
def faculty_Setup_GetAWSKeys(requests):
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
        # Save/Update Account_Number, Access_Key and Secret_Access_Key to AWS_Credentials
        try:
            credentialsObj = AWS_Credentials.objects.get(account_number=account_number)
            credentialsObj.access_key = access_key
            credentialsObj.secret_access_key = secret_access_key
            credentialsObj.save()
        except:
            credentialsObj = AWS_Credentials.objects.create(
                account_number=account_number,
                access_key=access_key,
                secret_access_key=secret_access_key,
            )
            credentialsObj.save()

    except:
        traceback.print_exc()
        # TO-DO: Put error messages here

    return faculty_Setup_Base(requests)


'''
Retrieval and storing of AMI length from instructor
returns to setup page
'''
def faculty_Setup_ShareAMI(requests):
    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    return faculty_Setup_Base(requests)


def student_Deploy_Base(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
    except:

        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    response["studentDeployBase"] = "active"


    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)

def student_Deploy_GetAccount(requests):

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
