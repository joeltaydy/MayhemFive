from Module_TeamManagement import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('home/', views.home, name='home'),
    path('upload/csv/', views.uploadcsv, name='uploadcsv'),
    path('student/team/', views.studTeam, name='sTeam'),
    path('student/stats/', views.studStats, name='sStats'),
    path('student/profile/', views.studProfile, name='sProfile'),
    path('instructor/team/', views.instOverview, name='instOverview'),
    path('instructor/profile/', views.instProfile, name='instProfile'),
]
