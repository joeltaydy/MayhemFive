from Module_TeamManagement import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('home/', views.home, name='home'),
    path('upload/csv/', views.uploadcsv, name='uploadcsv'),
    path('student/team/', views.studTeam, name='sTeam'),
    path('instructor/team/', views.instOverview, name='instuOverview'),
]
