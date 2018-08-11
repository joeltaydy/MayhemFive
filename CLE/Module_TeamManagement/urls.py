from Module_TeamManagement import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('home/', views.home, name='home'),
    # path('instructor/uploadcsv/', views.uploadcsv, name='uploadcsv'),
    path('instructor/uploadcsv/', views.configureDB_students, name='uploadcsv'),
    path('student/team/', views.student_Team, name='sTeam'),
    path('student/stats/', views.studStats, name='sStats'),
    path('student/profile/', views.student_Profile, name='sProfile'),
    path('instructor/team/', views.faculty_Overview, name='instOverview'),
    path('instructor/profile/', views.faculty_Profile, name='instProfile'),
    path('instructor/home/', views.faculty_Home, name='instHome'),
]
