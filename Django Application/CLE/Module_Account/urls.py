from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/', views.login, name='login'),
    url(r'^passwordMgmt/', views.passwordMgmt, name='passwordMgmt'),
    url(r'^logout/', views.logout, name='logout')
]
