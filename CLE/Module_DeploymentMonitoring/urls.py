from django.contrib import admin
from Module_DeploymentMonitoring import views
from django.urls import path

urlpatterns = [
    path('run_UAT_process/', views.run_UAT_Process, name='run_UAT_Process'),
]
