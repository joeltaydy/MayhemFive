from django.contrib import admin
from Module_EventConfig import views
from django.urls import path,re_path

urlpatterns = [
    path('instructor/ITOperationsLab/event/',views.faculty_Event_Base,name='itopslab_event'),
]
