from Module_TeamManagement import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('home/', views.home, name='home'),
    path('student/configTools/', views.configureDB_clt, name='uploadtoolStudent'),
    path('instructor/configTools/', views.configureDB_clt, name='uploadtools'),
    path('instructor/configStudents/', views.configureDB_course, name='uploadcsv'),
    path('instructor/configTeams/', views.configureDB_teams, name='uploadteam'), #wrong view
    path('student/team/', views.student_Team, name='sTeam'),
    path('student/stats/', views.studStats, name='sStats'),
    path('student/profile/', views.student_Profile, name='sProfile'),
    path('instructor/overview/', views.faculty_Overview, name='instOverview'),
    path('instructor/profile/', views.faculty_Profile, name='instProfile'),
    path('instructor/home/', views.faculty_Home, name='instHome'),
    path('instructor/notiMgmt/', views.ntmgmt, name = 'noti_mgmt' ),
    path('CLEAdmin/',views.CLEAdmin, name = 'cleAdmin'),
    path('CLEAdmin/moduleSetup',views.configureDB_faculty, name = 'modSu'),
    path('charts/',views.line_chart, name = 'charts_view'),
]
