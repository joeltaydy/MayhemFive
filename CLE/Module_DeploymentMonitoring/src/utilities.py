import boto3
from Module_DeploymentMonitoring.src import aws_config
from Module_DeploymentMonitoring.models import *
import json
import requests as req #for calling apis
from Module_TeamManagement.src.utilities import encode,decode


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

def getAllImages(account_number,access_key,secret_access_key):
    images = {}

    client = boto3.client('ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=aws_config.REGION
    )
    results = client.describe_images(
        Owners=[
            account_number,
        ],
    )

    for image in results['Images']:
        images[image['ImageId']] = image['Name']

    return images

def createAccount(accountNum, class_studentObj):
    class_studentObj= retrievalStudentClassObject(requests)
    try:
        awsC=AWS_Credentials.objects.get(account_number=accountNum)
    except:
        awsC = AWS_Credentials.objects.create(
            account_number=accountNum,
        )
        awsC.save()
    class_studentObj.awscredential = awsC
    class_studentObj.save()

def retrievalStudentClassObject(requests):
    student_email = requests.user.email
    courseList = requests.session['courseList_updated']
    for crse in courseList:
        if crse.course_title == "EMS201":
            coursesec = crse
    class_studentObj = Class.objects.get(student= student_email).get(course_section=coursesec)

    return class_studentObj

def addAWS(ipAddress,requests):
    class_studentObj= retrievalStudentClassObject(requests)
    awsC = class_studentObj.awscredential
    try:
        url = ipAddress+":8999/account/get/?secret_key=m0nKEY"
        response = req.get(url)
        jsonObj = json.loads(response.content.decode())
        awsC.access_key=encode(jsonObj['User']['Results']['aws_access_key_id '])
        awsC.secret_access_key = jsonObj['User']['Results']['aws_secret_access_key ']
        awsC.save()
    except:
        print("something wrong with request = AMS")


def addServerDetails(ipAddress,requests):
    class_studentObj= retrievalStudentClassObject(requests)
    awsC = class_studentObj.awscredential
    validity = validAccountNumber(ipAddress, awsC)
    if validity == False:
        raise Exception("Account number do not match with given IP, please try again")

    url = ipAddress+"/ec2/instance/get/current/?secret_key=m0nKEY"
    response = req.get(url)
    jsonObj = json.loads(response.content.decode())
    sd = Server_Details.objects.create(
        IP_address = ipAddress, 
        instanceid = jsonObj['Reservations'][0]['Instances'][0]['InstanceId'], 
        instanceName = "Faried",  
        state = "Live",

    )
    sd.save()


def validAccountNumber(ipAddress, awsCredentials):
    url = ipAddress+":8999/account/get/?secret_key=m0nKEY"
    response = req.get(url)
    jsonObj = json.loads(response.content.decode())
    return awsCredentials.account_number == jsonObj['User']['Account']