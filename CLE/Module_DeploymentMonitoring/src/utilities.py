import json
import boto3
import traceback
import requests as req
from Module_DeploymentMonitoring.src import aws_config
from Module_DeploymentMonitoring.models import *
from Module_TeamManagement.src.utilities import encode, decode
from Module_TeamManagement.models import *


# Get and connects to AWS SDK via boto3
def getEC2Client(access_key,secret_access_key,region_name=None):
    if region_name == None:
        region_name = aws_config.REGION

    client = boto3.client('ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )

    return client


# Get all team number and account number for those enrolled in course ESM201
def getAllTeamDetails():
    section_list = {}

    esm_course_sectionList = requests.session['courseList_update']['ESM201']
    for course_section in esm_course_sectionList:
        section_number = course_section['section_number']
        section_list[section_number] = {}

        query = Class.objects.filter(course_section=course_section['id']).values('team_number','awscredential').annotate(dcount=Count('team_number'))
        for team_details in query:
            team_name = team_details['team_number']
            account_number = team_details['awscredential']
            section_list[section_number].update(
                {
                    account_number:team_name
                }
            )

    return section_list


# Get all images from user account via Boto3
def getAllImages(client=None,account_number,access_key,secret_access_key):
    images = {}

    if client == None:
        client = getEC2Client(access_key,secret_access_key)

    results = client.describe_images(
        Owners=[
            account_number,
        ],
    )

    for image in results['Images']:
        images[image['ImageId']] = image['Name']

    return images


# Add user to Image launch permission
def addUserToImage(client=None,image_id,account_number,access_key,secret_access_key):
    if client == None:
        client = getEC2Client(access_key,secret_access_key)

    shared_response = client.modify_image_attribute(
        Attribute='launchPermission',
        ImageId=image_id,
        OperationType='add',
        UserIds=[
            account_number,
        ],
    )


# Remove user to Image launch permission
def removeUserFromImage(client=None,image_id,account_number,access_key,secret_access_key):
    if client == None:
        client = getEC2Client(access_key,secret_access_key)

    shared_response = client.modify_image_attribute(
        Attribute='launchPermission',
        ImageId=image_id,
        OperationType='remove',
        UserIds=[
            account_number,
        ],
    )


# Add AWS credentials for the relevant students
def addAWSCredentials(accountNum, class_studentObj):
    class_studentObj= getStudentClassObject(requests)
    try:
        awsC=AWS_Credentials.objects.get(account_number=accountNum)
    except:
        awsC = AWS_Credentials.objects.create(
            account_number=accountNum,
        )
        awsC.save()
    class_studentObj.awscredential = awsC
    class_studentObj.save()


# Retrieve the Class object that belongs under the current student user
def getStudentClassObject(requests):
    student_email = requests.user.email
    courseList = requests.session['courseList_updated']
    for course_title,course_details in courseList.items():
        if course_title == "EMS201":
            course_section_id = course_details['id']
    class_studentObj = Class.objects.get(student= student_email).get(course_section=course_section_id)

    return class_studentObj


# Add Access Keys and Secret Access Keys into the AWS credentials table
def addAWSKeys(ipAddress,requests):
    class_studentObj= getStudentClassObject(requests)
    awsC = class_studentObj.awscredential
    try:
        url = ipAddress+":8999/account/get/?secret_key=m0nKEY"
        response = req.get(url)
        jsonObj = json.loads(response.content.decode())
        awsC.access_key=encode(jsonObj['User']['Results']['aws_access_key_id '])
        awsC.secret_access_key = jsonObj['User']['Results']['aws_secret_access_key ']
        awsC.save()
    except:
        traceback.print_exc()
        print("something wrong with request = AMS")


# Add the server details into the server details table
def addServerDetails(ipAddress,requests):
    class_studentObj= getStudentClassObject(requests)
    awsC = class_studentObj.awscredential
    validity = validateAccountNumber(ipAddress, awsC)
    if validity == False:
        raise Exception("Account number do not match with given IP, please try again")

    url = ipAddress+"/ec2/instance/get/current/?secret_key=m0nKEY"
    response = req.get(url)
    jsonObj = json.loads(response.content.decode())
    sd = Server_Details.objects.create(
        IP_address = ipAddress,
        instanceid = jsonObj['Reservations'][0]['Instances'][0]['InstanceId'],
        instanceName = None,
        state = "Live",

    )
    sd.save()


# Validate if the IP address sent by the student user belongs under their account
def validateAccountNumber(ipAddress, awsCredentials):
    url = ipAddress+":8999/account/get/?secret_key=m0nKEY"
    response = req.get(url)
    jsonObj = json.loads(response.content.decode())
    return awsCredentials.account_number == jsonObj['User']['Account']
