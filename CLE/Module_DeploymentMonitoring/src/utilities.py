import json
import traceback
import requests as req
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from Module_DeploymentMonitoring.models import *
from Module_DeploymentMonitoring.forms import *
from Module_TeamManagement.models import *
from Module_TeamManagement.src import utilities


# Get all team number and account number for those enrolled in course ESM201
def getAllTeamDetails(course_sectionList):
    section_list = {}

    if len(course_sectionList) < 0 and 'EMS201' not in course_sectionList.keys():
        return {}

    for course_section in course_sectionList['EMS201']:
        section_number = course_section['section_number']
        section_list[section_number] = {}

        query = Class.objects.filter(course_section=course_section['id']).values('team_number','awscredential').annotate(dcount=Count('team_number'))
        for team_details in query:
            team_name = team_details['team_number']
            account_number = team_details['awscredential']

            if team_name != None and account_number != None:
                section_list[section_number][team_name] = account_number

    return section_list


# Add image detials into database. REturns an image_details object
def addImageDetials(image_id,image_name):
    image_detailsObj = Image_Details.objects.create(
        imageId=image_id,
        imageName=image_name,
    )
    image_detailsObj.save()
    return image_detailsObj


# Add AWS credentials for the relevant students
def addAWSCredentials(accountNum, requests):
    class_studentObj= getStudentClassObject(requests)
    try:
        awsC=class_studentObj.awscredential
        awsC.account_number = accountNum
        awsC.save()
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
    class_studentObj = Class.objects.filter(student= student_email).get(course_section=course_section_id)

    return class_studentObj


# Add Access Keys and Secret Access Keys into the AWS credentials table
def addAWSKeys(ipAddress,requests):
    class_studentObj= getStudentClassObject(requests)
    awsC = class_studentObj.awscredential
    try:
        url = 'http://'+ipAddress+":8999/account/get/?secret_key=m0nKEY"
        response = req.get(url)
        jsonObj = json.loads(response.content.decode())
        awsC.access_key = utilities.encode(jsonObj['User']['Results']['aws_access_key_id '])
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

    url = 'http://'+ipAddress+":8999/ec2/instance/get/current/?secret_key=m0nKEY"
    response = req.get(url)
    jsonObj = json.loads(response.content.decode())
    try: 
        sd = Server_Details.objects.create(
            IP_address = ipAddress,
            instanceid = jsonObj['Reservations'][0]['Instances'][0]['InstanceId'],
            instanceName = None,
            state = "Live",
            account_number=awsC
        )
        sd.save()
    except:
        raise Exception('duplicate IP address found in Database')


# Validate if the IP address sent by the student user belongs under their account
def validateAccountNumber(ipAddress, awsCredentials):
    url = 'http://'+ipAddress+":8999/account/get/?secret_key=m0nKEY"
    response = req.get(url)
    jsonObj = json.loads(response.content.decode())
    return awsCredentials.account_number == jsonObj['User']['Account']


# Adds and Updates GitHub link via form
def addGitHubLinkForm(request, form, template_name):
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


# TEMPORARY METHOD for mid-terms : Event Configuration
def runEvent(server_ip,server_id,event_type):
    payload = {'instance_id':server_id, 'secret_key':'m0nKEY'}
    successful_stoppage = []
    successful_count = 0

    unsuccessful_stoppage = []
    unsuccessful_count = 0

    results = {}

    if event_type == 'stop':
        server_url = 'http://' + server_ip + ":8999/ec2/instance/event/stop/"
    elif event_type == 'ddos':
        pass

    server_response = req.get(server_url, params=payload)
    server_jsonObj = json.loads(server_response.content.decode())

    if server_jsonObj['HTTPStatusCode'] == 200:
        successful_stoppage.append(server_id)
        successful_count += 1
    else:
        unsuccessful_stoppage.append(server_id)
        unsuccessful_count += 1

    results = {
        'successful':{
            'ids':successful_stoppage,
            'count':successful_count
        },
        'unsuccessful':{
            'ids':unsuccessful_stoppage,
            'count':unsuccessful_count
        }
    }

    return results
