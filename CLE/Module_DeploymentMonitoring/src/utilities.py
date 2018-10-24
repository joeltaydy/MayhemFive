
import csv
import pytz
import json
import traceback
import requests as req
from datetime import datetime
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from Module_DeploymentMonitoring.models import *
from Module_DeploymentMonitoring.forms import *
from Module_TeamManagement.models import *
from Module_EventConfig.models import *
from Module_TeamManagement.src.utilities import encode,decode
from Module_DeploymentMonitoring.src import aws_util

# Get all team number and account number for those enrolled in course ESM201
def getAllTeamDetails(course_sectionList):
    section_list = {}

    if len(course_sectionList) < 0 and 'EMS201' not in course_sectionList.keys():
        return {}

    for course_section in course_sectionList['EMS201']:
        section_number = course_section['section_number']
        section_list[section_number] = []

        query = Class.objects.filter(course_section=course_section['id']).values('team_number','awscredential').annotate(dcount=Count('team_number'))
        for team_details in query:
            team_name = team_details['team_number']
            account_number = team_details['awscredential']

            if team_name != None and account_number != None:
                section_list[section_number].append(
                    {
                        'team_name':team_name,
                        'account_number':account_number
                    }
                )

    return section_list


# Add image detials into database. Returns an image_details object (FOR FIRST TIME)
def addImageDetails(image):
    image_id = image['Image_ID']
    image_name = image['Image_Name']
    permissions = image['Launch_Permissions']

    account_numbers = getRegisteredUsers(permissions)

    image_detailsObj = Image_Details.objects.create(
        imageId=image_id,
        imageName=image_name,
        sharedAccNum='_'.join(account_numbers),
    )
    image_detailsObj.save()

    for account_number in account_numbers:
        addImageToUser(image_detailsObj,account_number)

    return image_detailsObj


# Add Image to AWS_Credentials
def addImageToUser(image,account_number):
    credentialsObj = AWS_Credentials.objects.get(account_number=account_number)
    temp_querySet = credentialsObj.imageDetails.filter(imageId=image.imageId)
    if len(temp_querySet) == 0:
        credentialsObj.imageDetails.add(image)
        credentialsObj.save()


# Remove Image from AWS_Credentials
def removeImageFromAUser(image,account_number):
    try:
        credentialsObj = AWS_Credentials.objects.get(account_number=account_number)
        temp_querySet = credentialsObj.imageDetails.filter(imageId=image.imageId)
        if len(temp_querySet) != 0:
            credentialsObj.imageDetails.remove(image)
            credentialsObj.save()
    except:
        pass


# Supplements addImageDetails function. Returns a list of all registered account numbers from AWS
def getRegisteredUsers(permissions):
    account_numbers = []

    for permission in permissions:
        user_id = permission['UserId']

        try:
            AWS_Credentials.objects.get(account_number=user_id)
            if user_id not in account_numbers:
                account_numbers.append(user_id)

        except:
            pass

    return account_numbers


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
    print(teamAddition)
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
    class_studentObj = Class.objects.filter(student=student_email).get(course_section=course_section_id)

    return class_studentObj


# Retrieve the Class object that belongs under the current student user
def getTeamMembersClassQuerySet(requests):
    team_name = getStudentClassObject(requests).team_number
    print(team_name)
    if team_name == None:
        return [getStudentClassObject(requests)]

    courseList = requests.session['courseList_updated']

    for course_title,course_details in courseList.items():
        if course_title == "EMS201":
            course_section_id = course_details['id']

    querySet = Class.objects.filter(course_section=course_section_id).filter(team_number=team_name)

    return querySet


# Add Access Keys and Secret Access Keys into the AWS credentials table
def addAWSKeys(ipAddress,requests):
    class_studentObj= getStudentClassObject(requests)
    awsC = class_studentObj.awscredential
    try:
        url = 'http://'+ipAddress+":8999/account/get/?secret_key=m0nKEY"
        response = req.get(url)
        jsonObj = json.loads(response.content.decode())
        awsC.access_key = encode(jsonObj['User']['Results']['aws_access_key_id '])
        awsC.secret_access_key = encode(jsonObj['User']['Results']['aws_secret_access_key '])
        awsC.save()
    except:
        traceback.print_exc()
        print("something wrong with request = AMS")


# Add the server details into the server details table
def addServerDetails(ipAddress,server_type,requests=None,account_number=None):
    if requests != None:
        class_studentObj= getStudentClassObject(requests)
        awsC = class_studentObj.awscredential
        validity = validateAccountNumber(ipAddress, awsCredentials=awsC)

    if account_number != None:
        validity = validateAccountNumber(ipAddress, account_number=account_number)

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
            account_number=awsC,
            type=server_type
        )
        sd.save()
    except:
        sd = Server_Details.objects.get(IP_address = ipAddress)
        sd.account_number =awsC
        sd.save()

    initiateStartServerTime(ipAddress)


# Saves the start time state of a server that is just set up
# Input: elastic IP Address of instance
# Output: Nil
def initiateStartServerTime(ipAddress):
    tz = pytz.timezone('Asia/Singapore')
    now = str(datetime.now(tz=tz))[:19]

    try:
        eventList = Event_Details.objects.filter(server_details=ipAddress,event_type="start").order_by("id").reverse()
        if len(eventList) == 0:
            event_Entry = Event_Details.objects.create(
                event_type="start",
                server_details=Server_Details.objects.get(IP_address=ipAddress),
                event_startTime=now,
                event_endTime=now,
                event_recovery=0
            )
            event_Entry.save()
            print(event_Entry)
    except:
        traceback.print_exc()


# Validate if the IP address sent by the student user belongs under their account
def validateAccountNumber(ipAddress, awsCredentials=None, account_number=None):
    url = 'http://'+ipAddress+":8999/account/get/?secret_key=m0nKEY"
    response = req.get(url)
    jsonObj = json.loads(response.content.decode())

    if account_number != None:
        return account_number == jsonObj['User']['Account']

    if awsCredentials != None:
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


# Adds and Updated Server Details via form
def addServerDetailsForm(request, form, template_name):
    data = dict()

    if request.method == 'POST':
        classObj = getStudentClassObject(request)
        credentialsObj = classObj.awscredential

        account_number = credentialsObj.account_number
        access_key = decode(credentialsObj.access_key)
        secret_access_key = decode(credentialsObj.secret_access_key)

        server_ip = request.POST.get('IP_address')
        server_id = request.POST.get('instanceid')

        server_is_valid = aws_util.validateServer(server_ip,server_id,access_key=access_key,secret_access_key=secret_access_key)

        if form.is_valid() and server_is_valid:
            form.save()

            serverObj = Server_Details.objects.get(IP_address=server_ip)
            serverObj.account_number = credentialsObj
            serverObj.save()

            data['form_is_valid'] = True
            servers = getAllServer(account_number)
            data['html_server_list'] = render_to_string('dataforms/serverdetails/partial_server_list.html', {'servers': servers})
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


# Obtain http status code and web server status of a group project based on account number.
# Returns the response object along with the statuses of the server and webapplication
#
def getMonitoringStatus(account_number, team_number, response):
    servers = Server_Details.objects.filter(account_number=account_number)
    for server in servers:
        server_ip = server.IP_address
        server_state = server.state
        server_name = server.instanceName
        server_type = server.type

        # Step 1: Check if server is alive
        server_state = getServerStatus(server)
        if server_state == 'Killed':
            server.delete()
            continue

        server_statistics = getServerStatistics(server_ip)
        response['server_status'].append(
            {
                'team_name':team_number,
                'server_ip':server_ip,
                'server_state':server_state,
                'server_name':server_name if server_name != None else '',
                'server_type':server.type,
                'breakdowns': server_statistics['Breakdowns'],
                'mtbf': server_statistics['MTBF'],
                'mttr': server_statistics['MTTR']
            }
        )

        # Step 2: Update server.state on server status
        server.state = server_state
        server.save()

        if server_state == 'Live':
            # Step 3: IF server 'Live', then check if webapp is 'Live'
            try:
                webapp_url = 'http://' + server_ip + ":8000/supplementary/health_check/"
                webapp_response = req.get(webapp_url)

                if webapp_response.status_code == 404:
                    response['webapp_status'].append(
                        {
                            'team_name':team_number,
                            'ip_address':server_ip,
                            'webapp_state':'Down'
                        }
                    )
                else:
                    webapp_jsonObj = json.loads(webapp_response.content.decode())

                    if webapp_jsonObj['HTTPStatusCode'] == 200:
                        response['webapp_status'].append(
                            {
                                'team_name':team_number,
                                'ip_address':server_ip,
                                'webapp_state':'Live'
                            }
                        )

            except req.ConnectionError as e:
                response['webapp_status'].append(
                    {
                        'team_name':team_number,
                        'ip_address':server_ip,
                        'webapp_state':'Down'
                    }
                )

        else:
            # Step 4: ELSE webapp is definitely 'Down'
            response['webapp_status'].append(
                {
                    'team_name':team_number,
                    'ip_address':server_ip,
                    'webapp_state':'Down'
                }
            )

    return response


# Gets the statistics of a server based on ip_address against event_details table
# Statistics obtained includes MTTR, MTBF, Breakdowns
#
def getServerStatistics(server_ip):
    from Module_EventConfig.models import Event_Details
    from Module_EventConfig.src.utilities import recoveryTimeCaclulation



    try:
        serverInitiateTime = Event_Details.objects.filter(server_details=server_ip).get(event_type="start").event_startTime
        tz = pytz.timezone('Asia/Singapore')
        now = str(datetime.now(tz=tz))[:19]

        serverEventList = Event_Details.objects.filter(server_details=server_ip).exclude(event_type="start")
        totalDownTime = 0
        for event in serverEventList:
            if event.event_recovery != None:
                totalDownTime = totalDownTime+float(event.event_recovery) #required for mttr
        totalUpTime = max(recoveryTimeCaclulation(serverInitiateTime, now) - totalDownTime,0) #required for mtbf
        mttr= str(totalDownTime/len(serverEventList))
        mtbf = str(totalUpTime/len(serverEventList))
        serverStatistics = {"Breakdowns": len(serverEventList), "MTTR": timeToString(mttr) , "MTBF" :timeToString(mtbf) }
    except:
        # traceback.print_exc()
        serverStatistics = {"Breakdowns": 0, "MTTR": 0, "MTBF" : 0}

    return serverStatistics


def timeToString(minutes):
    minute = int(minutes.split(".")[0])
    try:
        seconds = float("0."+minutes.split(".")[1])* 60
    except:
        seconds = 0
    day=0
    hours=0
    while minute > 60:
        if minute > 3600:
            day = minute//3600
            minute = minute % 3600
        elif minute > 60:
            hours = minute//60
            minute = minute % 60
    timeString = ""
    if day >0 :
        timeString = timeString +  str(day)+" Days "
    if hours> 0:
        timeString= timeString + str(hours) + " Hours "
    if minute>0:
        timeString=timeString+ str(minute) + " Minutes "
    timeString=timeString + str(seconds).split(".")[0] + " Seconds "
    return timeString

# Rule of thumb method - To check server status
#
def getServerStatus(server):
    server_state = server.state
    stu_credentials = server.account_number

    # Rule of thumb, if webapp is alive, then server will most definitely be alive
    # BUT if server is alive, there's no guarantee that webapp is alive
    access_key = decode(stu_credentials.access_key)
    secret_access_key = decode(stu_credentials.secret_access_key)

    resource = aws_util.getResource(access_key,secret_access_key,service='ec2')
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


# Retrieve metric of the specific server
#
def getMetric(server_ip,response):
    server = Server_Details.objects.get(IP_address=server_ip)
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


# Get all server ip registered under that account number
#
def getAllServer(account_number):
    server_ips = []

    querySet = Server_Details.objects.filter(account_number=account_number)
    for server in querySet:
        server_ips.append(
            {
                'server_ip':server.IP_address,
                'server_id':server.instanceid,
                'server_name':server.instanceName,
                'server_type':server.type
            }
        )

    return server_ips
