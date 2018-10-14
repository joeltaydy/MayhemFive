import traceback
from django.shortcuts import render
from django.http import HttpResponse
from Module_EventConfig import tasks
from Module_TeamManagement.models import *
from Module_Account.src import processLogin
from Module_DeploymentMonitoring.models import *
from Module_DeploymentMonitoring import views as views_DM
from Module_DeploymentMonitoring.src import utilities as utilities_DM


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
    datetime = requests.POST.get('datetime')

    try:
        team_details = utilities_DM.getAllTeamDetails(course_sectionList)
        for section_number in section_numberList:
            for team_name,account_number in team_details[section_number].items():
                querySet_serverList = Server_Details.objects.filter(account_number=account_number)
                for server in querySet_serverList:
                    server_ip = server.IP_address
                    server_id = server.instanceid

                    event_response = utilities_DM.runEvent(server_ip,server_id,event_type)
                    print(event_response)
                    # Not sure what to do with the event_response yet

                    return views_DM.faculty_Monitor_Base(requests)

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during event execution: ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)
