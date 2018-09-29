import traceback
from django.shortcuts import render
from django.http import HttpResponse

'''
Main function for setup page on faculty.
Will retrieve work products and render to http page
'''
def faculty_Setup_Base(requests):
    response = {"ITOpsLabSetup" : "active"}
    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)

'''
Retrieval and storing of github deployment package link from instructor
returns to setup page
'''
def faculty_Setup_GetGitHub(requests):

    return faculty_Setup_Base(requests)

'''
Retrieval and storing of AWS keys from instructor
returns to setup page
'''
def faculty_Setup_GetAWSKeys(requests):

    return faculty_Setup_Base(requests)

'''
Retrieval and storing of AMI length from instructor
returns to setup page
'''
def faculty_Setup_ShareAMI(requests):

    return faculty_Setup_Base(requests)

def student_Deploy_Base(requests):
    response = {"ITOpsLabStudentDeploy" : "active"}
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)

def student_Deploy_GetAccount(requests):

    return HttpResponse('')

def student_Deploy_GetIP(requests):

    return HttpResponse('')

def ITOpsLabMonitor(requests):
    response = {"ITOpsLabMonitor" : "active"}
    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)

def ITOpsLabEvent(requests):
    response = {"ITOpsLabEvent" : "active"}
    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)

def ITOpsLabStudentDeploy(requests):
    response = {"ITOpsLabStudentDeploy" : "active"}
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)

def ITOpsLabStudentMonitor(requests):
    response = {"ITOpsLabStudentMonitor" : "active"}
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentMonitor.html", response)
