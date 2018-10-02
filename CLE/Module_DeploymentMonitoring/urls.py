from django.contrib import admin
from Module_DeploymentMonitoring import views
from django.urls import path

urlpatterns = [
    path('instructor/ITOperationsLab/setup/',views.faculty_Setup_Base,name='itopslab_setup'),
    path('instructor/ITOperationsLab/setup/github/',views.faculty_Setup_GetGitHub,name='itopslab_setup_GitHub'),
    path('instructor/ITOperationsLab/setup/awskeys/',views.faculty_Setup_GetAWSKeys,name='itopslab_setup_AWSKeys'),
    path('instructor/ITOperationsLab/setup/ami/',views.faculty_Setup_ShareAMI,name='itopslab_setup_AMI'),
    path('instructor/ITOperationsLab/monitor/',views.ITOpsLabMonitor,name='itopslab_monitor'),
    path('instructor/ITOperationsLab/event/',views.ITOpsLabEvent,name='itopslab_event'),
    path('student/ITOperationsLab/deploy/',views.student_Deploy_Base,name='itopslab_studeploy'),
    path('student/ITOperationsLab/deploy/2',views.student_Deploy_Upload,name='itopslab_studeployUpload'),
    #path('student/ITOperationsLab/deploy/account/',views.student_Deploy_GetAccount,name='itopslab_studeploy_Account'),
    #path('student/ITOperationsLab/deploy/ip/',views.student_Deploy_GetIP,name='itopslab_studeploy_IP'),
    path('student/ITOperationsLab/monitor/',views.ITOpsLabStudentMonitor,name='itopslab_stumonitor'),
]
