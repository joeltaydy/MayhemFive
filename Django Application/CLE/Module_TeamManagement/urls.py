from django.conf.urls import url
import views

urlpatterns = [
    url(r'^home/', views.home, name='home'),
    url(r'^$', views.home, name ='index' ),
    url(r'^login/', views.login, name='login'),
    url(r'^login/loading', views.login_validation, name='login_validation'),
    url(r'^upload/csv/', views.uploadcsv, name='uploadcsv'),
    url(r'^upload/csv/loading',views.upload_csv,name='upload_csv'),
]
