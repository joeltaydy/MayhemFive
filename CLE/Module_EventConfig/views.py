import traceback
from django.shortcuts import render
from django.http import HttpResponse
from Module_EventConfig import tasks
from datetime import timedelta, datetime
from Module_TeamManagement.models import *
from Module_Account.src import processLogin
from Module_DeploymentMonitoring.models import *
from Module_DeploymentMonitoring import views as views_DM
from Module_DeploymentMonitoring.src import utilities as utilities_DM

# Test to see if django-background-tasks is wokring or not
#
def test(requests):
    value = requests.GET.get('message')
    period = requests.GET.get('period')

    if value == None:
        return HttpResponse('Please sepcify a message and a period (default 0 seconds).')

    if period == None:
        period = 0
    else:
        period = int(period)

    try:
        tasks.test_tasks(str(value), schedule=timedelta(seconds=period))

    except Exception as e:
        traceback.print_exc()
        return HttpResponse('Background tasks NOT successfully initiated')

    return HttpResponse('Background tasks successfully initiated')


# Main function for event configuration page on faculty.
#
def faculty_Event_Base(requests):
    response = {"faculty_Event_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)
    course_sectionList = requests.session['courseList_updated']

    response['course_sectionList'] = course_sectionList['EMS201']
    response['first_section'] = course_sectionList['EMS201'][0]['section_number']

    # Second round retrieval
    section_numberList = requests.POST.getlist('section_number')
    event_type = requests.POST.get('event_type')
    scheduled_datetime = datetime.now() if requests.POST.get('datetime') == None else requests.POST.get('datetime')

    if section_numberList == None or event_type == None:
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)

    try:
        serverList = []
        team_details = utilities_DM.getAllTeamDetails(course_sectionList)
        for section_number in section_numberList:
            for details in team_details[section_number]:
                querySet_serverList = Server_Details.objects.filter(account_number=details["account_number"])
                for server in querySet_serverList:
                    serverList.append(
                        {
                            'server_ip':server.IP_address,
                            'server_id':server.instanceid,
                            'server_account':server.account_number.account_number
                        }
                    )

        period = scheduled_datetime - datetime.now()
        if event_type == 'stop':
            tasks.stopServer(server_list=serverList, schedule=period)
        elif event_type == 'ddos':
            tasks.ddosAttack(server_list=serverList, schedule=period)

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during event execution: ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)

    requests.section_number = response['first_section']
    return views_DM.faculty_Monitor_Base(requests)
