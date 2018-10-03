from django.contrib import admin
from Module_DeploymentMonitoring import views
from django.urls import path,re_path

urlpatterns = [
    path('instructor/ITOperationsLab/setup/',views.faculty_Setup_Base,name='itopslab_setup'),
    path('instructor/ITOperationsLab/dps/',views.faculty_Setup_GetGitHubLinks,name='dp_list'),
    path('instructor/ITOperationsLab/dps/create/', views.faculty_Setup_AddGitHubLinks, name='dp_create'),
    path('instructor/ITOperationsLab/dps/<str:pk>/update/', views.faculty_Setup_UpdateGitHubLinks, name='dp_update'),
    path('instructor/ITOperationsLab/dps/<str:pk>/delete/', views.faculty_Setup_DeleteGitHubLinks, name='dp_delete'),
    path('instructor/ITOperationsLab/setup/awskeys/',views.faculty_Setup_GetAWSKeys,name='itopslab_setup_AWSKeys'),
    path('instructor/ITOperationsLab/setup/ami/',views.faculty_Setup_ShareAMI,name='itopslab_setup_AMI'),
    path('instructor/ITOperationsLab/monitor/',views.faculty_Monitor_Base,name='itopslab_monitor'),
    path('instructor/ITOperationsLab/event/',views.faculty_Event_Base,name='itopslab_event'),
    path('student/ITOperationsLab/deploy/',views.student_Deploy_Base,name='itopslab_studeploy'),
    path('student/ITOperationsLab/deploy/2',views.student_Deploy_Upload,name='itopslab_studeployUpload'),
    #path('student/ITOperationsLab/deploy/account/',views.student_Deploy_GetAccount,name='itopslab_studeploy_Account'),
    #path('student/ITOperationsLab/deploy/ip/',views.student_Deploy_GetIP,name='itopslab_studeploy_IP'),
    path('student/ITOperationsLab/monitor/',views.ITOpsLabStudentMonitor,name='itopslab_stumonitor'),
    # test
    path('instructor/ITOperationsLab/servers/',views.server_list,name='server_list'),
    path('instructor/ITOperationsLab/servers/create/', views.server_create, name='server_create'),
    path('instructor/ITOperationsLab/servers/<int:pk>/update/', views.server_update, name='server_update'),
    path('instructor/ITOperationsLab/servers/<int:pk>/delete/', views.server_delete, name='server_delete'),
    #deployment package forms

]
