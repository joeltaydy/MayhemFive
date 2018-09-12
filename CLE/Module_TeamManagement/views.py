import os
import traceback
import datetime
from zipfile import ZipFile
from django.shortcuts import render
from Module_TeamManagement.src import bootstrap, utilities, tele_util
from Module_TeamManagement.models import *
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from telethon.errors import PhoneNumberUnoccupiedError

from random import randint
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView
from django.http import HttpResponse

# Required for verification
from Module_Account.src import processLogin
from django.contrib.auth import logout, login

from Module_TeamManagement import forms
import logging
logr = logging.getLogger(__name__)
#Async form submission
from Module_TeamManagement.forms import PhoneNumberForm
from django.views.generic import FormView
from Module_TeamManagement.mixins import AjaxFormMixin

# Student Home Page
#@login_required(login_url='/')
def home(requests):
    context = {}
    # Redirect user to login page if not authorized and student
    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',context)
    context["home"] = "active"

    student_email = requests.user.email
    all_SocialAccount = SocialAccount.objects.all()

    for each_SocialAccount in all_SocialAccount:
        data = each_SocialAccount.extra_data
        if data['email'] == student_email:
            requests.session['user_picture'] = data['picture']
            requests.session['user_name'] = data['name'].replace('_','').strip()

    # Populates the info for the side nav bar for instructor
    utilities.populateRelevantCourses(requests, studentEmail=student_email)

    # Reads web scrapper results
    trailResults = utilities.populateTrailheadInformation(requests, student_email)
    context.update(trailResults)

    # Get number of weeks since school term start and reamining weeks till school term ends
    past_weeks, remaining_weeks = utilities.getRemainingWeeks()

    if past_weeks != None and remaining_weeks != None:
        context['past_weeks'] = past_weeks
        context['remaining_weeks'] = remaining_weeks
        context['progress'] = past_weeks/remaining_weeks * 100
    else:
        context['past_weeks'] = 0
        context['remaining_weeks'] = 0
        context['progress'] = 0

    # Get telegram group/channel link
    enrolled_classes = Class.objects.filter(student=student_email)
    context['telegram'] = {'status' : 'False'}
    for enrolled_class in enrolled_classes:
        group_link = enrolled_class.telegram_grouplink
        channel_link = enrolled_class.telegram_channellink

        if group_link != None:
            context['telegram']['status'] = 'True'
            try:
                context['telegram']['group'].update({enrolled_class.course_section : group_link})
            except:
                context['telegram']['group'] = {enrolled_class.course_section : group_link}

        if channel_link != None:
            context['telegram']['status'] = 'True'
            try:
                context['telegram']['channel'].update({enrolled_class.course_section : channel_link})
            except:
                context['telegram']['channel'] = {enrolled_class.course_section : channel_link}
    #print(context)
    return render(requests,"Module_TeamManagement/Student/studentHome.html",context)


# Admin homepage
#@login_required(login_url='/')
def CLEAdmin(requests):
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else:
        context["home_page"] = "active"
        return render(requests,"Administrator/admindashboard.html",context)
    # return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)


# Faculty Home Page
#@login_required(login_url='/')
def faculty_Home(requests):
    context = {}
    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',context)

    context = {"faculty_Home" : "active"}

    faculty_username = requests.user.email.split('@')[0]

    all_SocialAccount = SocialAccount.objects.all()

    for each_SocialAccount in all_SocialAccount:
        data = each_SocialAccount.extra_data
        if data['email'] == requests.user.email:
            requests.session['user_picture'] = data['picture']
            requests.session['user_name'] = data['name'].replace('_','').strip()

    #print(requests.user.email)
    try:
        courseStudents = []
        #Populates the info for the side nav bar for instructor
        utilities.populateRelevantCourses(requests, instructorEmail=requests.user.email)
        facultyObj = Faculty.objects.get(email=requests.user.email)
        registered_course_section = facultyObj.course_section.all()
        courses = {}
        students = []
        previouscourse = "a"
        for course_section in registered_course_section:
            course_title = course_section.course.course_title
            if course_title not in courses:
                courses[course_title]= {}
                if previouscourse != "a":
                    courses[previouscourse]["count"] = len(courseStudents)
                    courses[previouscourse]["sectionCount"] = sectionCounter
                courseStudents=[]
                previoussection = "a"
                previouscourse = course_title
                sectionCounter = 0

            if previoussection != course_section:
                sectionCounter += 1

            classObj = Class.objects.all().filter(course_section=course_section)

            for student in classObj:
                students.append(student)
                courseStudents.append(student)

            previoussection = course_section

        if previouscourse != "a":
            courses[previouscourse]["count"] = len(courseStudents)
            courses[previouscourse]["sectionCount"] = sectionCounter

        context['section_count'] = len(registered_course_section)
        context['course_count'] = len(courses)
        context['course_list'] = courses
        context['student_count'] = len(students)

    except:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        context = {'messages' : ['Invalid user account']}
        return render(requests,'Module_Account/login.html',context)

    context["courses"] = requests.session['courseList']

    # Get number of weeks since school term start and reamining weeks till school term ends
    past_weeks, remaining_weeks = utilities.getRemainingWeeks()

    if past_weeks != None and remaining_weeks != None:
        context['past_weeks'] = past_weeks
        context['remaining_weeks'] = remaining_weeks
        context['progress'] = past_weeks/remaining_weeks * 100
    else:
        context['past_weeks'] = 0
        context['remaining_weeks'] = 0
        context['progress'] = 0

    # Reads web scrapper results
    trailResults = utilities.populateTrailheadInformation(requests, instructorEmail=requests.user.email)
    context.update(trailResults)
    context['message'] = 'Successful retrieval of faculty\'s overview information'
    return render(requests, "Module_TeamManagement/Instructor/instructorHome.html",context)


# Faculty Student Management Page
#@login_required(login_url='/')
def faculty_Overview(requests):

    context = {}
    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',context)

    context = {"faculty_Overview" : "active", 'course' : {}}

    faculty_email = requests.user.email

    if requests.method == "GET":
        course_section = requests.GET.get('module').replace(" ", "")
    else:
        course_section = requests.POST.get('course_section')
    facultyObj = Faculty.objects.get(email=faculty_email)
    classObj_list = Class.objects.all().filter(course_section=course_section)

    trailResults = utilities.populateTrailheadInformation(requests, instructorEmail=requests.user.email)
    context.update(trailResults)
    if len(classObj_list) > 0:
        classList = [] # Containing student class objects
        for enrolled_class in classObj_list:
            studentInfo = {}
            studentInfo['team'] = enrolled_class.team_number
            studentInfo['info'] =  enrolled_class.student #Obtains student model from Foreign key
            studentUserName = enrolled_class.student.username
            studentPointsPosition = trailResults['CourseTrailResults']['class']['Students_Information']['students'].index(studentUserName)
            studentInfo['points'] = trailResults['CourseTrailResults']['class']['Students_Information']['points'][studentPointsPosition]
            studentInfo['badges'] = trailResults['CourseTrailResults']['class']['Students_Information']['badges'][studentPointsPosition]
            classList.append(studentInfo)
        context['course']['classList'] = classList

    course_section = Course_Section.objects.get(course_section_id=course_section)
    if course_section.section_number == 'G0':
        context['module'] = course_section.course.course_title
    else:
        context['module'] = course_section.course.course_title + " " + course_section.section_number
    context['user'] = facultyObj
    context['message'] = 'Successful retrieval of faculty\'s profile'
    return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)


# TO-DO: update function
# @login_required(login_url='/')
def studStats(requests):
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    # Redirect user to login page if not authorized and student
    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',context)
    context = {"stud_stats" : "active"}
    return render(requests,"Module_TeamManagement/Student/studentStatistics.html",context)


# Student Team Page
# @login_required(login_url='/')
def student_Team(requests):
    context = {}
    # Redirect user to login page if not authorized and student
    try:
        processLogin.studentVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',context)

    context = {"student_Team" : "active", 'course' : {}}
    studentList = []
    module = requests.GET.get('module')
    student_email =requests.user.email
    student_username = student_email.split('@')[0]

    if student_username == None:
        context['message'] = 'Please specify a username'
        return render(requests,"Module_TeamManagement/Student/studentTeam.html", context)

    studentObj = Student.objects.get(username=student_username)
    classObj = Class.objects.all().filter(student=studentObj , course_section = module ) #Will return queryset containing 1 row unless has multiple teams in same class


    for enrolled_class in classObj: #Should contain 1 row
        if(enrolled_class.team_number != None ):
            team_list = Class.objects.all().filter(team_number=enrolled_class.team_number).filter(course_section=enrolled_class.course_section).exclude(student=studentObj)
            for student_class_model in team_list:
                studentList.append(student_class_model.student) #List containing student models

            context['team'] = studentList

    # Reads web scrapper results
    trailResults = utilities.populateTrailheadInformation(requests, student_email)
    context.update(trailResults)

    context['module'] = classObj[0].course_section.course_section_id
    context['user'] = studentObj
    context['message'] = 'Successful retrieval of student\'s team'
    return render(requests,"Module_TeamManagement/Student/studentTeam.html",context)


# This is for initial configuration by superadmin
# This function populates the database with the fauclty members and the courses
#
# Requests param: POST
# - file
#
# Models to populate:
# - Course
# - Faculty
# - School_Term
#
# Response (Succcess):
# - configureDB_faculty
# - results
# - message
#
def configureDB_faculty(requests):
    response = {"configureDB_faculty" : "active"}
    if requests.method == "GET":
        return render(requests, "Administrator/uploadcsv.html", response)

    bootstrapFile = {}
    try:
        file = requests.FILES.get("file", False)
        action = requests.POST.get("action")
        start_date = requests.POST.get("start_date")
        end_date = requests.POST.get("end_date")

        if not utilities.validateDate(start_date) or not utilities.validateDate(end_date):
            raise Exception("Incorrect date format, should be YYYY-MM-DD")

        bootstrapFile['start_date'] = start_date
        bootstrapFile['end_date'] = end_date

        if action != None:
            bootstrap.clear_Database()

        if file.name.endswith('.zip'):
            unzipped = ZipFile(file)
            unzipped.extractall(os.path.abspath('bootstrap_files'))
            bootstrapFile['file_type'] = 'zip'

            for fileName in unzipped.namelist():
                if fileName.lower() == 'faculty_information.xlsx':
                    bootstrapFile['faculty'] = os.path.abspath('bootstrap_files/' + fileName)
                elif fileName.lower() == 'course_information.xlsx':
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

        else:
            raise Exception("Invalid file type. Please upload .xlsx or .zip only")

        # If file is .xlsx or .zip then proceed with processing
        response['results'] =  bootstrap.bootstrap_Faculty(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Administrator/uploadcsv.html", response)

    response['message'] = 'Successful Upload'
    return render(requests, "Administrator/uploadcsv.html", response)


# This is for initial configuration by faculty
# This function associates the course witht he faculty member
#
# Requests param: POST
# - course_title
# - file
#
# Models to populate:
# - Faculty_course_section
# - Course_Section
#
# Models to modify:
# - Faculty
# - Course_Section
#
# Response (Succcess):
# - configureDB_course
# - courses
# - message
#
def configureDB_course(requests):
    response = {"configureDB_course" : "active"}

    # Retrieve all the course
    courseObject = Course.objects.all()
    courseList = []

    for course in courseObject:
        courseList.append(course.course_title)
    response['courses'] = courseList

    if requests.method == "GET":
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)

    try:
        file = requests.FILES.get("file", False)
        if file:
            return configureDB_students(requests)

        course_title = requests.POST.get("course_title")
        facultyObj = Faculty.objects.get(email=requests.user.email)
        courseObj = Course.objects.get(course_title=course_title)
        course_section_id = course_title + 'G0'

        # Create/Retrieve (if exists) course_section object
        try:
            course_sectioObj = Course_Section.objects.get(course_section_id=course_section_id)
        except:
            course_sectioObj = Course_Section.objects.create(
                course_section_id=course_section_id,
                course=courseObj,
                section_number='G0',
            )
            course_sectioObj.save()

        # Associate course with faculty
        facultyObj.course_section.add(course_sectioObj)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        # traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)

    # Reflush the nav bar
    utilities.populateRelevantCourses(requests, instructorEmail=requests.user.email)

    response['message'] = 'Course created'
    return faculty_Home(requests)


# This is for subsequent configuration by faculty
# This function populates the database with the students information
#
# Requests param: POST
# - file
# - course_title
#
# Models to populate:
# - Students
# - Course_Section
# - Class
#
# Models to modify:
# - Faculty
#
# Response (Succcess):
# - configureDB_students
# - results
# - message
#
def configureDB_students(requests):
    response = {"configureDB_students" : "active"}

    # Retrieve all the course
    courseObject = Course.objects.all()
    courseList = []

    for course in courseObject:
        courseList.append(course.course_title)
    response['courses'] = courseList

    if requests.method == "GET":
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)

    try:
        file = requests.FILES.get("file", False)
        faculty_username = requests.user.email.split('@')[0]
        course_title = requests.POST.get("course_title")
        bootstrapFile = {}

        if file.name.endswith('.xlsx'):
            if 'student_information' in file.name.lower():
                bootstrapFile['course_title'] = course_title
                bootstrapFile['faculty_username'] = faculty_username
                bootstrapFile['file_path'] = file.temporary_file_path()

            else:
                raise Exception("Invalid file information. Please upload students information only.")

        else:
            raise Exception("Invalid file type. Please upload .xlsx only")

        # If file is .xlsx then proceed with processing
        response['results'] =  bootstrap.bootstrap_Students(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        # traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)

    # Reflush the nav bar
    utilities.populateRelevantCourses(requests, instructorEmail=requests.user.email)

    response['message'] = 'Successful Upload'
    # return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)
    return faculty_Home(requests)


# This is for subsequent configuration by faculty
# This function configures the students team based on a excel file
#
# Requests param: POST
# - file
#
# Models to populate:
# - NONE
#
# Models to modify:
# - Class
#
# Response (Succcess):
# - configureDB_teams
# - results
# - message
#
def configureDB_teams(requests):
    response = {"configureDB_teams" : "active"}
    if requests.method == "GET":
        utilities.populateRelevantCourses(requests,instructorEmail=requests.user.email)
        response['courses'] = requests.session['courseList']
        return render(requests, "Module_TeamManagement/Instructor/instructorTeams.html", response)

    try:
        file = requests.FILES.get("file", False)
        faculty_email = requests.user.email
        course_section = requests.POST.get("course_section")
        bootstrapFile = {}

        if file.name.endswith('.xlsx'):
            if 'team_information' in file.name.lower():
                bootstrapFile['faculty_email'] = faculty_email
                bootstrapFile['course_section'] = course_section
                bootstrapFile['file_path'] = file.temporary_file_path()

            else:
                raise Exception("Invalid file information. Please upload teams information only.")

        else:
            raise Exception("Invalid file type. Please upload .xlsx only")

        # If file is .xlsx then proceed with processing
        response['results'] = bootstrap.update_Teams(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        response['message'] = e.args[0]
        # return render(requests, "Module_TeamManagement/Instructor/instructorOverview.html", response)
        return faculty_Overview(requests)

    response['message'] = 'Teams Configured'
    # return render(requests, "Module_TeamManagement/Instructor/instructorOverview.html", response)
    return faculty_Overview(requests)


# This is for subsequent configuration by faculty
# This function configures the CLT with the associate student
#
# Requests param: POST
# - file
# - course_title
#
# Models to populate:
# - Cloud_Learning_Tools
#
# Models to modify:
# - Class
#
# Response (Succcess):
# - configureDB_clt
# - results
# - message
#
def configureDB_clt(requests):
    response = {"configureDB_clt" : "active"}

    if requests.method == "GET" and requests.GET.get("user") == "faculty":
        utilities.populateRelevantCourses(requests,instructorEmail=requests.user.email)
        response['courses'] = requests.session['courseList']
        return render(requests, "Module_TeamManagement/Instructor/instructorTools.html", response)

    elif requests.method == "GET" and (requests.GET.get("user") == "student" or requests.POST.get("user") == "student"):
        utilities.populateRelevantCourses(requests,studentEmail=requests.user.email)
        response['courses'] = requests.session['courseList']
        return render(requests, "Module_TeamManagement/Student/studentTools.html", response)

    try:
        user = requests.POST.get("user")

        if user == "student":
            student_email = requests.user.email
            type = requests.POST.get("type")
            link = requests.POST.get("link")
            course = requests.POST.get("course_title")

            if course == None:
                raise Exception('Please specfy a course.')
            elif type == None:
                raise Exception('Please specfy a learning tool type.')
            elif len(link) == 0:
                raise Exception('Please specfy a learning tool link.')

            id = student_email.split('@')[0] + "_" + type
            class_studentObj = Class.objects.filter(student=student_email).filter(course_section=course)
            try:
                # Update
                cltObj = Cloud_Learning_Tools.objects.get(id=id)
                cltObj.website_link = link
                cltObj.save()
            except:
                # Create
                cltObj = Cloud_Learning_Tools.objects.create(
                    id=id,
                    type=type,
                    website_link=link,
                )
                cltObj.save()

            for student in class_studentObj:
                student.clt_id.add(cltObj)

            return home(requests)

        file = requests.FILES.get("file", False)
        faculty_email = requests.user.email
        action = requests.POST.get("action")
        bootstrapFile = {}

        if action == 'batch':
            course = requests.POST.get("course_title")
        else:
            course = requests.POST.get("course_section")

        if file.name.endswith('.xlsx'):
            if 'learning_tools' in file.name.lower():
                bootstrapFile['faculty_email'] = faculty_email
                bootstrapFile['course'] = course
                bootstrapFile['action'] = action
                bootstrapFile['file_path'] = file.temporary_file_path()

            else:
                raise Exception("Invalid file information. Please upload teams information only.")

        else:
            raise Exception("Invalid file type. Please upload .xlsx only")

        # If file is .xlsx then proceed with processing
        response['results'] = bootstrap.update_CLT(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        response['message'] = e.args[0]
        if requests.POST.get("user") == "student":
            utilities.populateRelevantCourses(requests,studentEmail=requests.user.email)
            response['courses'] = requests.session['courseList']
            return render(requests, "Module_TeamManagement/Student/studentTools.html", response)

        if action == 'batch':
            utilities.populateRelevantCourses(requests,instructorEmail=requests.user.email)
            response['courses'] = requests.session['courseList']
            return render(requests, "Module_TeamManagement/Instructor/instructorTools.html", response)

        else:
            return faculty_Overview(requests)

    response['message'] = 'Learning Tools Configured'
    if action == 'batch':
        utilities.populateRelevantCourses(requests,instructorEmail=requests.user.email)
        response['courses'] = requests.session['courseList']
        return render(requests, "Module_TeamManagement/Instructor/instructorTools.html", response)
    else:
        return faculty_Overview(requests)


# This is for subsequent configuration by faculty
# This function authenticates the faculty and creates the channels/groups
#
# Requests param: GET
# - phone_number
#
# Models to modify:
# - Class
#
# Response (Succcess):
# - configure_telegram
# - results
# - message
#
class PhoneNumberFormView(AjaxFormMixin, FormView):
    form_class = PhoneNumberForm
    template_name  = 'Module_TeamManagement/Instructor/instructorTools.html'
    success_url = '/form-success/'

def configureDB_telegram(requests):
    response = {"configure_telegram" : "active"}
    if requests.method == "GET":
        utilities.populateRelevantCourses(requests,instructorEmail=requests.user.email)
        response['courses'] = requests.session['courseList']
        return render(requests, "Module_TeamManagement/Instructor/instructorTools.html", response)

    try:
        username = requests.user.email.split('@')[0]
        phone_number = requests.POST.get('phone_number')
        login_code = requests.POST.get('login_code')

        if len(phone_number) == 8:
            phone_number = str('+65') + phone_number

        client = tele_util.getClient(username)
        client.connect()

        if not client.is_user_authorized():
            if phone_number != None and login_code == None:
                client.send_code_request(phone_number)

                facultyObj = Faculty.objects.get(username=username)
                encrypt_phone_number = utilities.encode(phone_number)
                facultyObj.phone_number = encrypt_phone_number
                facultyObj.save()

                return HttpResponse('')

            elif phone_number != None and login_code != None:
                try:
                    client.sign_in(phone=phone_number, code=login_code)
                except PhoneNumberUnoccupiedError:
                    client.sign_up(phone=phone_number, code=login_code)

        # Creation to channel/groups. IF action == NONE, this whole portion will be skipped
        action = requests.POST.get('action')
        course_section = requests.POST.get('course_section')

        if action == 'create_sectionChannel':
            course_sectionObj = Course_Section.objects.get(course_section_id=course_section)
            class_QuerySet = Class.objects.filter(course_section=course_section)

            results = tele_util.initialize_Channel(
                client=client,
                course_title=course_sectionObj.course.course_title,
                section_number=course_sectionObj.section_number,
            )

            for student in class_QuerySet:
                student.telegram_channellink = results['channel_link']
                student.save()

            response['message'] = results['message']
            return faculty_Overview(requests)

        elif action == 'create_sectionGroup':
            course_sectionObj = Course_Section.objects.get(course_section_id=course_section)
            class_QuerySet = Class.objects.filter(course_section=course_section)

            results = tele_util.initialize_Group(
                client=client,
                course_title=course_sectionObj.course.course_title,
                section_number=course_sectionObj.section_number,
            )

            for student in class_QuerySet:
                student.telegram_grouplink = results['group_link']
                student.save()

            response['message'] = results['message']
            return faculty_Overview(requests)

        elif action == 'create_teamGroup':
            course_sectionObj = Course_Section.objects.get(course_section_id=course_section)
            class_QuerySet = Class.objects.filter(course_section=course_section)

            teams = {}
            for student in class_QuerySet:
                try:
                    teams[student.team_number].append(student)
                except:
                    teams[student.team_number] = [student]

            for team_number,students in teams.items():
                results = tele_util.initialize_Group(
                    client=client,
                    course_title=course_sectionObj.course.course_title,
                    section_number=course_sectionObj.section_number,
                    team_number=team_number,
                )
                for student in students:
                    student.telegram_grouplink = results['group_link']
                    student.save()

            response['message'] = 'Teams Telegram Group Configured'
            return faculty_Overview(requests)

        tele_util.disconnectClient(client)


    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        utilities.populateRelevantCourses(requests,instructorEmail=requests.user.email)
        response['courses'] = requests.session['courseList']
        response['message'] = e.args[0]
        return render(requests, "Module_TeamManagement/Instructor/instructorTools.html", response)

    # Need to double confirm where to direct the user to once done.
    response['message'] = 'Telegram Account Configured'
    return render(requests, "Module_TeamManagement/Instructor/instructorTools.html", response)


line_chart = TemplateView.as_view(template_name='Module_TeamManagement\line_chart.html')


#multistep form for telegram Setup
class TelegramWizard(SessionWizardView):
    template_name = "Module_TeamManagement/Instructor/telegram.html"

    def done(self, form_list, **kwargs):
        form_data = process_form_data(form_list)

        return render(self.request, 'Module_TeamManagement/Instructor/done.html', {'form_data': form_data})


def process_form_data(form_list):
    form_data = [form.cleaned_data for form in form_list]

    logr.debug(form_data[0]['phone_number'])
    logr.debug(form_data[1]['login_code'])

    #add in method to return the validation Code
    return form_data
