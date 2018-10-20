from django.contrib import admin
from Module_DeploymentMonitoring import views
from django.urls import path,re_path

urlpatterns = [
    path('instructor/ITOperationsLab/setup/deployment_package/',views.faculty_Setup_GetGitHubLinks,name='dp_list'),
    path('instructor/ITOperationsLab/setup/deployment_package/create/', views.faculty_Setup_AddGitHubLinks, name='dp_create'),
    path('instructor/ITOperationsLab/setup/deployment_package/<str:pk>/update/', views.faculty_Setup_UpdateGitHubLinks, name='dp_update'),
    path('instructor/ITOperationsLab/setup/deployment_package/<str:pk>/delete/', views.faculty_Setup_DeleteGitHubLinks, name='dp_delete'),
    path('instructor/ITOperationsLab/setup/awskeys/',views.faculty_Setup_GetAWSKeys,name='itopslab_setup_AWSKeys'),
    path('instructor/ITOperationsLab/monitor/',views.faculty_Monitor_Base,name='itopslab_monitor'),
    path('student/ITOperationsLab/deploy/',views.student_Deploy_Base,name='itopslab_studeploy'),
    path('student/ITOperationsLab/deploy/2',views.student_Deploy_Upload,name='itopslab_studeployUpload'),
     path('student/ITOperationsLab/deploy/standard/',views.student_Deploy_Base_std,name='itopslab_studeploystd'),
    #path('student/ITOperationsLab/deploy/account/',views.student_Deploy_GetAccount,name='itopslab_studeploy_Account'),
    #path('student/ITOperationsLab/deploy/ip/',views.student_Deploy_GetIP,name='itopslab_studeploy_IP'),
    path('student/ITOperationsLab/monitor/',views.student_Monitor_Base,name='itopslab_stumonitor'),

    # For retrieving and sharing of AMI
    path('instructor/ITOperationsLab/setup/',views.faculty_Setup_Base,name='itopslab_setup'),
    path('instructor/ITOperationsLab/setup/ami/get/',views.faculty_Setup_GetAMI,name='itopslab_setup_AMI_get'),
    path('instructor/ITOperationsLab/setup/ami/accounts/get/',views.faculty_Setup_GetAMIAccounts,name='itopslab_setup_AMI_Accounts_get'),
    path('instructor/ITOperationsLab/setup/ami/accounts/share/',views.faculty_Setup_ShareAMI,name='itopslab_setup_AMI_Accounts_share'),
]
