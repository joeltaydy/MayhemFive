from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.welcome, name='welcome'),
    url(r'^login/', views.login, name='login'),
    url(r'^home/', views.home, name='home'),
]
