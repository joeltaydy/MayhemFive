import os
import traceback
from zipfile import ZipFile
from django.shortcuts import render
from Module_TeamManagement.src import bootstrap
from Module_TeamManagement.models import Student, Faculty, Class, Course_Section, Course, Cloud_Learning_Tools
from django.contrib.auth.decorators import login_required

#@login_required(login_url='/')
def home(requests): #student home page
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
        context["home_page"] = "active"
        return render(requests,"Module_TeamManagement/Student/studentHome.html",context)
    # return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

#@login_required(login_url='/')
def instHome(requests): #student home page
    context = {"home_page" : "active"}
    return render(requests,"Module_TeamManagement/Instructor/instructorHome.html",context)
    # return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

#@login_required(login_url='/')
def instOverview(requests): #instructor overview page
    context = {}
    results = {}
    assistantList = []

    email = requests.GET.get('email')

    if email == None:
        email = 'sample.instructor.1@smu.edu.sg'

    instructor = Instructor.objects.get(email=email)
    sections = instructor.section.all()

    for section in sections:
        teams = Assigned_Team.objects.all().filter(section=section)
        assistantList.append(Teaching_Assistant.objects.get(section=section))
        results[section.section_number] = {}

        for team in teams:
            try:
                results[section.section_number][team.team_number].append(team.student)
            except:
                results[section.section_number][team.team_number] = [team.student]

    context['section_list'] = 'active'
    context['assistants'] = assistantList
    context['results'] = results

    return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

#@login_required(login_url='/')
def studTeam(requests): # student team view page
    context = {}
    studentList = []

    email = requests.GET.get('email')

    if email == None:
        email = 'sample.1@smu.edu.sg'

    team_number = Assigned_Team.objects.get(student=email).team_number
    section = Assigned_Team.objects.get(student=email).section
    team = Assigned_Team.objects.all().filter(team_number=team_number).filter(section=section)

    for member in team:
        studentList.append(member.student)

    context['team_list'] = 'active'
    context['results'] = studentList
    context['section_number'] = section.section_number
    context['team_number'] = team_number

    return render(requests,"Module_TeamManagement/Student/studentTeam.html",context)

#@login_required(login_url='/')
def studStats(requests):
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
        context = {"stud_stats" : "active"}
        return render(requests,"Module_TeamManagement/Student/studentStatistics.html",context)

#@login_required(login_url='/')
def studProfile(requests):
    context = {"stud_profile" : "active"}

    username = requests.GET.get('username')

    if username == None:
        username = 'sample.1'

    student = Student.objects.get(username=username)
    assigned_team = Assigned_Team.objects.get(student=student)

    context['user'] = student
    context['team_number'] = assigned_team.team_number
    context['section_number'] = assigned_team.section.section_number

    return render(requests,"Module_TeamManagement/Student/studentProfile.html",context)

#@login_required(login_url='/')
def instProfile(requests):
    context = {"inst_profile" : "active"}

    username = requests.GET.get('username')

    if username == None:
        username = 'sample.instructor.1'

    context['user'] = Instructor.objects.get(username=username)

    return render(requests,"Module_TeamManagement/Instructor/instructorProfile.html", context)

# Newly added by Faried, 07.08.2018
# This is for initial configuration by superadmin
#
# requests parameters:
# - file
#
# Models to populate:
# - Course
# - Course_Section  (Optional)
# - Faculty
#
# response (Succcess):
# - Number of course
# - Number of sections for each course (Optional)
# - Number of faculty
#
def configureDB_admin(requests):
    context = {"upload_csv" : "active"}
    if requests.method == "GET":
        return render(requests, "<path to html page>", context)

    try:
        file = requests.FILES.get("file", False)
        bootstrapFile = {}

        if file.name.endswith('.zip'):
            unzipped = ZipFile(file)
            unzipped.extractall(os.path.abspath('bootstrap_files'))
            bootstrapFile['file_type'] = 'zip'

            for fileName in unzipped.namelist():
                if fileName.lower() == 'faculty_information.xlsx' or fileName.lower() == 'faculty_information.csv' :
                    bootstrapFile['faculty'] = os.path.abspath('bootstrap_files/' + fileName)
                elif fileName.lower() == 'course_information.xlsx' or fileName.lower() == 'course_information.csv':
                    bootstrapFile['course'] = os.path.abspath('bootstrap_files/' + fileName)

            if 'faculty' not in bootstrapFile.keys() or 'course' not in bootstrapFile.keys():
                raise Exception("Invalid file information within .zip file. Please upload faculty or course information only.")

        elif file.name.endswith('.xlsx'):
            if file.name.lower() == 'faculty_information.xlsx':
                bootstrapFile['file_path'] = file.temporary_file_path()
                bootstrapFile['file_type'] = 'excel'
                bootstrapFile['file_information'] = 'faculty'

            elif file.name.lower() == 'course_information.xlsx':
                bootstrapFile['file_path'] = file.temporary_file_path()
                bootstrapFile['file_type'] = 'excel'
                bootstrapFile['file_information'] = 'course'

            else:
                raise Exception("Invalid file information. Please upload faculty or course information only.")

        elif file.name.endswith('.csv'):
            if file.name.lower() == 'faculty_information.csv':
                bootstrapFile['file_path'] = file.temporary_file_path()
                bootstrapFile['file_type'] = 'csv'
                bootstrapFile['file_information'] = 'faculty'

            elif file.name.lower() == 'course_information.csv':
                bootstrapFile['file_path'] = file.temporary_file_path()
                bootstrapFile['file_type'] = 'csv'
                bootstrapFile['file_information'] = 'faculty'

            else:
                raise Exception("Invalid file information. Please upload faculty or course information only.")

        else:
            raise Exception("Invalid file type. Please upload .csv or .xlsx or .zip only")

        # If file is .csv or .xlsx or .zip then proceed with processing
        bootstrap.bootstrap(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        # return render(requests, "<path to html page>", {"error":e.args[0]})

    # return render(requests, "<path to html page>", {"message": "Successful Upload"})


# Newly added by Faried, 07.08.2018
# This is for subsequent configuration by faculty
#
# requests parameters:
# - file
# - course_title
# - section_number
#
# Models to populate:
# - Students
# - Class
#
# response (Succcess):
# - Number of student
#
def configureDB_faculty(requests):
    context = {"upload_csv" : "active"}
    if requests.method == "GET":
        return render(requests, "<path to html page>", context)

    try:
        file = requests.FILES.get("file", False)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        # traceback.print_exc()
        return render(requests, "<path to html page>", {"error":e.args[0]})

    return render(requests, "<path to html page>", {"message": "Successful Upload"})
