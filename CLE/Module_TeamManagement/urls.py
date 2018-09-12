from Module_TeamManagement import views
from django.contrib import admin
from django.urls import path
from Module_TeamManagement.forms import PhoneNumberForm, VerificationCodeForm
from Module_TeamManagement.views import TelegramWizard, PhoneNumberFormView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('student/configTools/', views.configureDB_clt, name='uploadtoolStudent'),
    path('instructor/configTools/', views.configureDB_clt, name='uploadtools'),
    path('instructor/configStudents/', views.configureDB_course, name='uploadcsv'),
    path('instructor/configTeams/', views.configureDB_teams, name='uploadteam'),
    path('student/team/', views.student_Team, name='sTeam'),
    path('student/stats/', views.studStats, name='sStats'),
    path('instructor/overview/', views.faculty_Overview, name='instOverview'),
    path('instructor/home/', views.faculty_Home, name='instHome'),
    path('CLEAdmin/',views.CLEAdmin, name = 'cleAdmin'),
    path('CLEAdmin/moduleSetup',views.configureDB_faculty, name = 'modSu'),
    path('charts/',views.line_chart, name = 'charts_view'),
    # path('instructor/telegram_setup/', TelegramWizard.as_view(FORMS, condition_dict={'verificationcode': views.enter_phonenumber}), name='telegram_setup'),
    # path('instructor/telegram_setup/', TelegramWizard.as_view([PhoneNumberForm, VerificationCodeForm]), name='telegram_setup'),
    path('instructor/telegram_setup/', views.configureDB_telegram, name='telegram_setup'),
    path('join/', PhoneNumberFormView.as_view(), name='phone_number_form'),
]
