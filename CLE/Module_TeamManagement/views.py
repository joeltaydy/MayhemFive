import os
import traceback
from zipfile import ZipFile
from django.shortcuts import render
from Module_TeamManagement.src import bootstrap, tele_util, utilities
from Module_TeamManagement.models import Student, Faculty, Class, Course_Section, Course, Cloud_Learning_Tools
from django.contrib.auth.decorators import login_required


# TO-DO: update function
#@login_required(login_url='/')
def home(requests): #student home page
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else:
        #Populates the info for the side nav bar for instructor
        utilities.populateRelevantCourses(requests, studentEmail=requests.user.email)

        context["home_page"] = "active"
        return render(requests,"Module_TeamManagement/Student/studentHome.html",context)

# TO-DO: update function
# Add notification management page
#@login_required(login_url='/')
def ntmgmt(requests): #instructor notification page
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else:
        context["noti_mgmt"] = "active"
        return render(requests,"error404.html",context)
    # return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)


# TO-DO: update function
# Add admin management page
#@login_required(login_url='/')
def CLEAdmin(requests): #instructor notification page
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


# TO-DO: update function
#@login_required(login_url='/')
def faculty_Home(requests): #student home page
    try:
    #Populates the info for the side nav bar for instructor
        utilities.populateRelevantCourses(requests, instructorEmail=requests.user.email)
    except:
        context = {'messages' : ['Invalid user account']}
        return render(requests,'Module_Account/login.html',context)

    context = {"faculty_Home" : "active", "courses" :requests.session['courseList'] }
    return render(requests, "Module_TeamManagement/Instructor/instructorHome.html",context)


# Updated by Faried, 11.08.2018
# Requests param : GET
# - username
#
# Response context : Dictionary
# - faculty_profile
# - course_list
# - user
# - message
#
# @login_required(login_url='/')
def faculty_Profile(requests):
    context = {"faculty_profile" : "active", 'course_list' : {}}

    faculty_username = requests.GET.get('username')
    # faculty_username = 'sample.instructor.1'

    if faculty_username == None:
        context['message'] = 'Please specify a username'
        return render(requests,"Module_TeamManagement/Instructor/instructorProfile.html", context)

    facultyObj = Faculty.objects.get(username=faculty_username)
    course_sectionList = facultyObj.course_section.all()

    if len(course_sectionList) > 1:
        for course_section in course_sectionList:
            try:
                context['course_list'][course_section.course.course_title].append(course_section)
            except:
                context['course_list'][course_section.course.course_title] = [course_section]
    else:
        context['course_list'][course_section.course.course_title] = [course_section]

    context['user'] = facultyObj
    context['message'] = 'Successful retrieval of faculty\'s profile'
    return render(requests,"Module_TeamManagement/Instructor/instructorProfile.html", context)


# Updated by Faried, 11.08.2018
# Requests param : GET
# - username
#
# Response context : Dictionary
# - faculty_Overview
# - course
# - user
# - message
#
#@login_required(login_url='/')
def faculty_Overview(requests):
    context = {"faculty_Overview" : "active", 'course' : {}}

    faculty_email = requests.user.email
    course = requests.GET.get('module')
    # faculty_username = 'sample.instructor.1'
    '''
    if faculty_username == None:
        context['message'] = 'Please specify a username'
        return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html", context)
    '''

    facultyObj = Faculty.objects.get(email=faculty_email)
    course_section = Class.objects.filter(course_section=course)

    if len(course_section) > 0:
        classList = [] # Containing student class objects
        for enrolled_class in course_section:
            studentInfo = {}
            studentInfo['grade'] = enrolled_class.grades
            studentInfo['score'] = enrolled_class.score
            studentInfo['team'] = enrolled_class.team_number
            studentInfo['info'] =  enrolled_class.student #Obtains student model from Foreign key
            classList.append(studentInfo)
        context['course']['classList'] = classList

    '''
    if len(course_section) > 0:
        for enrolled_class in course_section:
            context['course'][enrolled_class.course_section_id] = {}
            students = Class.objects.all().filter(course_section=enrolled_class)
            for student in students:
                if student.team_number != None:
                    try:
                        context['course'][enrolled_class.course_section_id][student.team_number].append(student)
                    except:
                        context['course'][enrolled_class.course_section_id][student.team_number] = [student]
                else:
                    try:
                        context['course'][enrolled_class.course_section_id]['T0'].append(student)
                    except:
                        context['course'][enrolled_class.course_section_id]['T0'] = [student]
    else:
        context['course'][course_section.course_section_id] = {}
        students = Class.objects.all().filter(course_section=course_section)
        for student in students:
            if student.team_number != None:
                try:
                    context['course'][course_section.course_section_id][student.team_number].append(student)
                except:
                    context['course'][course_section.course_section_id][student.team_number] = [student]
            else:
                try:
                    context['course'][course_section.course_section_id]['T0'].append(student)
                except:
                    context['course'][course_section.course_section_id]['T0'] = [student]
    '''
    context['module'] = course
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
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else:
        context = {"stud_stats" : "active"}
        return render(requests,"Module_TeamManagement/Student/studentStatistics.html",context)


# Updated by Faried, 11.08.2018
# Requests param : GET
# - username
#
# Response context : Dictionary
# - student_Profile
# - course_list
# - user
# - message
#
# @login_required(login_url='/')
def student_Profile(requests):
    context = {"student_Profile" : "active", 'course_list' : {}}

    student_username = requests.GET.get('username')
    # student_username = 'sample.1'

    if student_username == None:
        context['message'] = 'Please specify a username'
        return render(requests,"Module_TeamManagement/Student/studentProfile.html", context)

    studentObj = Student.objects.get(username=student_username)
    classObjList = Class.objects.all().filter(student=studentObj)

    if len(classObjList) > 1:
        for classObj in classObjList:
            context['course_list'][classObj.course_section.course.course_title] = classObj
    else:
        context['course_list'][classObjList.course_section.course.course_title] = classObj

    context['user'] = studentObj
    context['message'] = 'Successful retrieval of student\'s profile'
    return render(requests,"Module_TeamManagement/Student/studentProfile.html",context)


# Updated by Faried, 11.08.2018
# Requests param : GET
# - username
#
# Response context : Dictionary
# - student_Team
# - course
# - user
# - message
#
# @login_required(login_url='/')
def student_Team(requests):
    context = {"student_Team" : "active", 'course' : {}}
    studentList = []

    student_username = requests.GET.get('username')
    # student_username = 'sample.1'

    if student_username == None:
        context['message'] = 'Please specify a username'
        return render(requests,"Module_TeamManagement/Student/studentTeam.html", context)

    studentObj = Student.objects.get(username=student_username)
    classObj = Class.objects.all().filter(student=studentObj)

    if len(classObj) > 1:
        for enrolled_class in classObj:
            team_list = Class.objects.all().filter(team_number=enrolled_class.team_number).filter(course_section=enrolled_class.course_section).exclude(student=studentObj)
            context['course'][enrolled_class.course_section.course_section_id] = team_list

    else:
        team_list = Class.objects.all().filter(team_number=classObj.team_number).filter(course_section=classObj.course_section).exclude(student=studentObj)
        context['course'][classObj.course_section.course.course_section_id] = team_list

    context['user'] = studentObj
    context['message'] = 'Successful retrieval of student\'s team'
    return render(requests,"Module_TeamManagement/Student/studentTeam.html",context)


# Newly added by Faried, 07.08.2018 - for bootstrap
# Updated by Faried, 10.08.2018
# This is for initial configuration by superadmin
#
# Requests param: POST
# - file
#
# Models to populate:
# - Course
# - Faculty
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

    try:
        file = requests.FILES.get("file", False)
        bootstrapFile = {}

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
        # traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Administrator/uploadcsv.html", response)

    response['message'] = 'Successful Upload'
    return render(requests, "Administrator/uploadcsv.html", response)


# Newly added by Faried, 11.08.2018
# This is for initial configuration by faculty
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
            configureDB_students(requests)
            return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)

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
    return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)


# Newly added by Faried, 07.08.2018 - for bootstrap
# Updated by Faried, 11.08.2018
# This is for subsequent configuration by faculty
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

    response['message'] = 'Successful Upload'
    return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", response)


# Newly added by Faried, 12.08.2018 - for bootstrap
# This is for subsequent configuration by faculty
#
# Requests param: POST
# - file
# - course_title
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
        return render(requests, "Module_TeamManagement/Instructor/<html page>", response)

    try:
        file = requests.FILES.get("file", False)
        faculty_username = requests.user.email.split('@')[0]
        course_title = requests.POST.get("course_title")
        bootstrapFile = {}

        if file.name.endswith('.xlsx'):
            if 'team_information' in file.name.lower():
                bootstrapFile['faculty_username'] = faculty_username
                bootstrapFile['course_title'] = course_title
                bootstrapFile['file_path'] = file.temporary_file_path()

            else:
                raise Exception("Invalid file information. Please upload teams information only.")

        else:
            raise Exception("Invalid file type. Please upload .xlsx only")

        # If file is .xlsx then proceed with processing
        response['results'] =  bootstrap.update_Teams(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        # traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Module_TeamManagement/Instructor/<html page>", response)

    response['message'] = 'Teams Configured'
    return render(requests, "Module_TeamManagement/Instructor/<html page>", response)


# Newly added by Faried, 13.08.2018 - for bootstrap
# This is for subsequent configuration by faculty
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
    response = {"configureDB_teams" : "active"}
    if requests.method == "GET":
        return render(requests, "Module_TeamManagement/Instructor/<html page>", response)

    try:
        file = requests.FILES.get("file", False)
        faculty_username = requests.user.email.split('@')[0]
        course_title = requests.POST.get("course_title")
        bootstrapFile = {}

        if file.name.endswith('.xlsx'):
            if 'cloud_learning_tools' in file.name.lower():
                bootstrapFile['faculty_username'] = faculty_username
                bootstrapFile['course_title'] = course_title
                bootstrapFile['file_path'] = file.temporary_file_path()

            else:
                raise Exception("Invalid file information. Please upload teams information only.")

        else:
            raise Exception("Invalid file type. Please upload .xlsx only")

        # If file is .xlsx then proceed with processing
        response['results'] =  bootstrap.update_CLT(bootstrapFile)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        # traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Module_TeamManagement/Instructor/<html page>", response)

    response['message'] = 'Learning Tools Configured'
    return render(requests, "Module_TeamManagement/Instructor/<html page>", response)


# Newly added by Faried, 13.08.2018
# This is for subsequent configuration by faculty
#
# Requests param: GET
# - course_title
# - section_number
# - username
#
# Models to modify:
# - Class
#
# Response (Succcess):
# - initialize_Section_Channel
# - results
# - message
#
def initialize_Section_Channel(request):
    response = {"initialize_Section_Channel" : "active"}
    if requests.method == "GET":
        return render(requests, "Module_TeamManagement/Instructor/<html page>", response)

    try:
        section_number = requests.GET.get("section_number")
        faculty_username = requests.GET.get("username")
        course_title = requests.GET.get("course_title")

        response['results'] = tele_util.initialize_Channel(faculty_username,course_title,section_number)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        # traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Module_TeamManagement/Instructor/<html page>", response)

    response['message'] = 'Telegram Channel for Section Created'
    return render(requests, "Module_TeamManagement/Instructor/<html page>", response)
