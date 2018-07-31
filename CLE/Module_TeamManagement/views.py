import os
import traceback
from zipfile import ZipFile
from django.shortcuts import render
from Module_TeamManagement.src import bootstrap
from Module_TeamManagement.models import Assigned_Team
from django.contrib.auth.decorators import login_required

@login_required(login_url='/')
def home(requests): #student home page
    context = {}
    return render(requests,"Module_TeamManagement/Student/studentHome.html",context)
    # return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

@login_required(login_url='/')
def instOverview(requests): #instructor overview page
    teams = Assigned_Team.objects.all().order_by('section')
    context = {}
    return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

@login_required(login_url='/')
def studTeam(requests): # student team view page
    sectionNo = 'G2'
    teams = teams = Assigned_Team.objects.filter(section = sectionNo)

    context = {"teamList" : teams}
    return render(requests,"Module_TeamManagement/Student/studentTeam.html",context)
@login_required(login_url='/')
def studStats(requests):
    return render(requests,"Module_TeamManagement/Student/studentStatistics.html")

@login_required(login_url='/')
def studProfile(requests):
    return render(requests,"Module_TeamManagement/Student/studentProfile.html")

@login_required(login_url='/')
def instProfile(requests):
    return render(requests,"Module_TeamManagement/Instructor/instructorProfile.html")

@login_required(login_url='/')
def uploadcsv(requests): # instructor bootstrap page
    if requests.method == "GET":
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", {})

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
