import json
import traceback
import requests as req
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from Module_DeploymentMonitoring.models import *
from Module_DeploymentMonitoring.forms import *
from Module_TeamManagement.models import *
from Module_TeamManagement.src.utilities import encode,decode
from Module_DeploymentMonitoring.src import aws_util


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
    teamAddition = requests.POST.get("isTeam") #if "" or None then is single add if not is a group add
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

    #Add to rest of team
    if teamAddition != None and teamAddition != "":
        classTeam = getTeamClassObject(requests) #returns a list of class student objects based on current user (exclude current user)
        for classStudent in classTeam:
            awsC=classStudent.awscredential
            awsC.account_number = accountNum
            awsC.save()
            classStudent.awscredential = awsC
            classStudent.save()


def getTeamClassObject(requests):
    student_email = requests.user.email
    courseList = requests.session['courseList_updated']
    for course_title,course_details in courseList.items():
        if course_title == "EMS201":
            course_section_id = course_details['id']
    class_studentObj = Class.objects.filter(student= student_email).get(course_section=course_section_id)
    class_teamObj = Class.objects.filter(course_section=course_section_id).filter(team_number = class_studentObj.team_number).exclude(student =class_studentObj.student)
    return class_teamObj


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
        # awsC.access_key = encode(jsonObj['User']['Results']['aws_access_key_id '])
        awsC.access_key = jsonObj['User']['Results']['aws_access_key_id ']
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
        sd = Server_Details.objects.get(IP_address = ipAddress)
        sd.account_number =awsC
        sd.save()


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


# Obtain http status code and web server status of a group project based on account number.
# Returns the response object along with the statuses of the server and webapplication
#
def getMonitoringStatus(account_number, team_number, response):
    # Assumption that there's only one server for one account
    server = Server_Details.objects.filter(account_number=account_number)[0]
    server_ip = server.IP_address
    server_state = server.state

    # Step 1: Check if server is alive
    server_state = getServerStatus(server)
    response['server_status'][team_number] = server_state

    # Step 2: Update server.state on server status
    server.state = server_state
    server.save()

    if server_state == 'Live':
        # Step 3: IF server 'Live', then check if webapp is 'Live'
        try:
            webapp_url = 'http://' + server_ip + ":8000/supplementary/health_check/"
            webapp_response = req.get(webapp_url)
            webapp_jsonObj = json.loads(webapp_response.content.decode())

            if webapp_jsonObj['HTTPStatusCode'] == 200:
                response['webapp_status'][team_number] = {'IP_Address':server_ip,'State':'Live'}

        except req.ConnectionError as e:
            response['webapp_status'][team_number] = {'IP_Address':server_ip,'State':'Down'}

    else:
        # Step 4: ELSE webapp is definitely 'Down'
        response['webapp_status'][team_number] = {'IP_Address':server_ip,'State':'Down'}

    return response


# Rule of thumb method - To check server status
#
def getServerStatus(server):
    server_state = server.state
    stu_credentials = server.account_number

    # Rule of thumb, if webapp is alive, then server will most definitely be alive
    # BUT if server is alive, there's no guarantee that webapp is alive

    # resource = aws_util.getResource(decode(stu_credentials.access_key),stu_credentials.secret_access_key,service='ec2')
    resource = aws_util.getResource(stu_credentials.access_key,stu_credentials.secret_access_key,service='ec2')
    instance = resource.Instance(server.instanceid)
    instance_state = instance.state

    http_status_code = instance_state['Code']

    if http_status_code == 16:
        server_state = 'Live'
    elif http_status_code == 0:
        server_state = 'Pending'
    elif http_status_code == 32 or http_status_code == 48:
        server_state = 'Killed'
    elif http_status_code == 80 or http_status_code == 64:
        server_state = 'Down'

    return server_state


def getMetric(account_number,response):
    server = Server_Details.objects.filter(account_number=account_number)[0]
    server_ip = server.IP_address
    server_state = server.state
    server_state = getServerStatus(server)

    # Step 2: Update server.state on server status
    server.state = server_state
    server.save()

    if server_state == 'Live':
        try:
            webapp_url = 'http://' + server_ip + ":8999/cloudwatch/metric/get/?namespace=AWS/EC2&name=NetworkIn&period=300"
            response["webapp_metric"]["network_metric"] = getCloudMetric(webapp_url)
            webapp_url = 'http://' + server_ip + ":8999/cloudwatch/metric/get/?namespace=AWS/EC2&name=CPUUtilization&period=300"
            response["webapp_metric"]["CPUutilization_metric"] = getCloudMetric(webapp_url)
        except:
            traceback.print_exc()

    return response


# collect cloud metrics based on cloudmetric list
# These tools can be found under /cloudwatch/metric/list/?namespace=AWS/EC2
# All have similiar structures
#
def getCloudMetric(webapp_url):
    webapp_response = req.get(webapp_url)
    webapp_jsonObj = json.loads(webapp_response.content.decode())
    label = "default"
    sortedValueList= []
    sortedKeyList=[]
    if webapp_jsonObj['HTTPStatusCode'] == 200:
        jsonResults = {}
        for datapoints in webapp_jsonObj["metric_statistics"]["Datapoints"]:
            jsonResults[datapoints["Timestamp"]] = datapoints["Average"]

        #Sorting out the values
        sortedKeyList = sorted(jsonResults)
        timeList = []
        sortedKeyList=sorted(sortedKeyList[len(sortedKeyList)-20:])
        for key in sortedKeyList:
            sortedValueList.append(jsonResults[key])
            time = key.split("T")[1][:-4]
            hour = int(time[:2])+8
            if hour >= 24:
                hour = hour -24
            time = str(hour) + time[2:]
            timeList.append(time)
        label = webapp_jsonObj["metric_statistics"]["Datapoints"][0]["Unit"]
    return {'xValue': timeList, 'yValue': sortedValueList, 'Label':label}
