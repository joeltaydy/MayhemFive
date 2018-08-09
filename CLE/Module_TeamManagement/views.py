import os
import traceback
from zipfile import ZipFile
from django.shortcuts import render
from Module_TeamManagement.src import bootstrap
from Module_TeamManagement.models import Assigned_Team
from django.contrib.auth.decorators import login_required


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

def instHome(requests): #instructor home page
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
        context = {"home_page" : "active"}
        return render(requests,"Module_TeamManagement/Instructor/instructorHome.html",context)


def instOverview(requests): #instructor overview page
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
        teams = Assigned_Team.objects.all().order_by('section')
        context = {"teamList" : teams, "team_list" : "active"}
        return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

def studTeam(requests): # student team view page
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
        sectionNo = 'G2'
        teams = teams = Assigned_Team.objects.filter(section = sectionNo)

        context = {"teamList" : teams, "team_list" : "active"}
        return render(requests,"Module_TeamManagement/Student/studentTeam.html",context)

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

def studProfile(requests):
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
        context = {"stud_profile" : "active"}
        return render(requests,"Module_TeamManagement/Student/studentProfile.html",context)


def instProfile(requests):
    '''
        Check if user is authenticated aka session
    '''
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
        context = {"inst_profile" : "active"}
        return render(requests,"Module_TeamManagement/Instructor/instructorProfile.html", context)

def uploadcsv(requests): # instructor bootstrap page
    context = {}
    if not requests.user.is_authenticated:
        return render(requests,'Module_Account/login.html',context)
    else: 
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
                bootstrapFile['file'] = file
                bootstrapFile['type'] = 'excel'
                bootstrapFile['user'] = 'student'

            elif file.name.lower() == 'instructor.xlsx': # FILENAME may change. Take note
                bootstrapFile['file'] = file
                bootstrapFile['type'] = 'excel'
                bootstrapFile['user'] = 'instructor'

            elif file.name.lower() == 'teaching_assistant.xlsx': # FILENAME may change. Take note
                bootstrapFile['file'] = file
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
