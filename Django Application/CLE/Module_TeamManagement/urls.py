from django.conf.urls import url
import views

urlpatterns = [
    url(r'^home/', views.home, name='home'),
    url(r'^upload/csv/', views.uploadcsv, name='uploadcsv'),
]
