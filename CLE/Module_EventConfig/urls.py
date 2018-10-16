from django.contrib import admin
from Module_EventConfig import views
from django.urls import path,re_path

urlpatterns = [
    path('background_tasks/test/',views.test,name='test'),
    path('instructor/ITOperationsLab/event/',views.faculty_Event_Base,name='itopslab_event'),
    path('event/start/', views.serverCall), #Temp endpoint
    path('event/recovery/', views.serverRecoveryCall),
]
