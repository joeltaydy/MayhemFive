from django.conf.urls import url
from Module_TeamManagement import views

urlpatterns = [
    url(r'^home/', views.home, name='home'),
    url(r'^upload/csv/', views.uploadcsv, name='uploadcsv'),
    url(r'^student/team/', views.studTeam, name='sTeam'),
    url(r'^instructor/team/', views.instOverview, name='instuOverview'),
]
