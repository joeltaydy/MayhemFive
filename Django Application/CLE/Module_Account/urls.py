from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/', views.login, name='login'),
    url(r'^password_reset/', views.password_reset, name='password_reset'),
    url(r'^logout/', views.logout, name='logout')
]
