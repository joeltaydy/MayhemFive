from zipfile import ZipFile
from django.shortcuts import render
from Module_TeamManagement.src import bootstrap
from Module_TeamManagement.models import Assigned_Team

def home(requests): #student home page
    context = {}
    return render(requests,"Module_TeamManagement/Student/studentHome.html",context)
    # return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

def instOverview(requests): #instructor overview page
    teams = Assigned_Team.objects.all().order_by('section')
    context = {"teamList" : teams}
    return render(requests,"Module_TeamManagement/Instructor/instructorOverview.html",context)

def studTeam(requests): # student team view page
    sectionNo = 'G2'
    teams = teams = Assigned_Team.objects.filter(section = sectionNo)

    context = {"teamList" : teams}
    return render(requests,"Module_TeamManagement/Student/studentTeam.html",context)

def studStats(requests):
    return render(requests,"Module_TeamManagement/Student/studentStatistics.html")

def studProfile(requests):
        return render(requests,"Module_TeamManagement/Student/studentProfile.html")

def instProfile(requests):
        return render(requests,"Module_TeamManagement/Instructor/instructorProfile.html")        

def uploadcsv(requests): # instructor bootstrap page
    if requests.method == "GET":
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", {})

    # If not GET, then proceed
    try:
        file = requests.FILES.get("file", False)
        bootstrapFile = {}

        if file.name.endswith('.zip'):
            unzipped = ZipFile(file)
            for fileName in unzipped.namelist():
                bootstrapFile['file_student'] = unzipped.read(fileName) if fileName == 'student.xlsx' else continue # FILENAME may change. Take note
                bootstrapFile['file_instructor'] = unzipped.read(fileName) if fileName == 'instructor.xlsx' else continue # FILENAME may change. Take note
            bootstrapFile['type'] = 'zip'

        elif file.name == 'student.xlsx': # FILENAME may change. Take note
            bootstrapFile['file'] = file
            bootstrapFile['type'] = 'excel'
            bootstrapFile['user'] = 'student'

        elif file.name == 'instructor.xlsx': # FILENAME may change. Take note
            bootstrapFile['file'] = file
            bootstrapFile['type'] = 'excel'
            bootstrapFile['user'] = 'instructor'

        else:
            raise Exception("File is not .xlsx or .zip type")

        # If file is .xlsx or .zip then proceed with processing
        bootstrap.bootstrap(bootstrapFile)

    except Exception as e:
        return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", {"error":e.args[0]})

    return render(requests, "Module_TeamManagement/Instructor/uploadcsv.html", {"message": "Successful Upload"})
