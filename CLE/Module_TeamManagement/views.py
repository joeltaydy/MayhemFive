import os
import traceback
from zipfile import ZipFile
from django.shortcuts import render
from Module_TeamManagement.src import bootstrap
from Module_TeamManagement.models import Student, Instructor, Section, Assigned_Team, Teaching_Assistant
from django.contrib.auth.decorators import login_required

#@login_required(login_url='/')
def home(requests): #student home page
    context = {"home_page" : "active"}
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

#@login_required(login_url='/')
def uploadcsv(requests): # instructor bootstrap page
    context = {"upload_csv" : "active"}
    if requests.method == "GET":
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", context)

    # If not GET, then proceed
    try:
        file = requests.FILES.get("file", False)
        bootstrapFile = {}

        if file.name.endswith('.zip'):
            unzipped = ZipFile(file)
            unzipped.extractall(os.path.abspath('bootstrap_files'))

            for fileName in unzipped.namelist():
                if fileName.lower() == 'student.xlsx':
                    bootstrapFile['file_student'] = os.path.abspath('bootstrap_files/' + fileName)
                elif fileName.lower() == 'instructor.xlsx':
                    bootstrapFile['file_instructor'] = os.path.abspath('bootstrap_files/' + fileName)
                elif fileName.lower() == 'teaching_assistant.xlsx':
                    bootstrapFile['file_assistant'] = os.path.abspath('bootstrap_files/' + fileName)

            bootstrapFile['type'] = 'zip'

        elif file.name.lower() == 'student.xlsx': # FILENAME may change. Take note
            bootstrapFile['file'] = file.temporary_file_path()
            bootstrapFile['type'] = 'excel'
            bootstrapFile['user'] = 'student'

        elif file.name.lower() == 'instructor.xlsx': # FILENAME may change. Take note
            bootstrapFile['file'] = file.temporary_file_path()
            bootstrapFile['type'] = 'excel'
            bootstrapFile['user'] = 'instructor'

        elif file.name.lower() == 'teaching_assistant.xlsx': # FILENAME may change. Take note
            bootstrapFile['file'] = file.temporary_file_path()
            bootstrapFile['type'] = 'excel'
            bootstrapFile['user'] = 'assistant'

        else:
            raise Exception("File is not .xlsx or .zip type")

        # If file is .xlsx or .zip then proceed with processing
        bootstrap.bootstrap(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        # traceback.print_exc()
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", {"error":e.args[0]})

    return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", {"message": "Successful Upload"})
