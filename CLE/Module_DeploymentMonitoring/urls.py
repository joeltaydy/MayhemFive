from django.contrib import admin
from Module_DeploymentMonitoring import views
from django.urls import path

urlpatterns = [
    
    path('student/ITOperationsLab/deploy',views.ITOpsLabStudentDeploy,name='itopslab_studeploy'),
    path('student/ITOperationsLab/monitor',views.ITOpsLabStudentMonitor,name='itopslab_stumonitor'),
    path('instructor/ITOperationsLab/setup',views.ITOpsLabSetup,name='itopslab_setup'),
    path('instructor/ITOperationsLab/monitor',views.ITOpsLabMonitor,name='itopslab_monitor'),
    path('instructor/ITOperationsLab/event',views.ITOpsLabEvent,name='itopslab_event'),
]
