from django.conf.urls import url
import views

urlpatterns = [
    url(r'^login/', views.login, name='login'),
    url(r'^home/', views.home, name='home'),
    url(r'^upload/csv/', views.uploadcsv, name='uploadcsv'),
    url('',views.upload_csv,name='upload_csv')
]
