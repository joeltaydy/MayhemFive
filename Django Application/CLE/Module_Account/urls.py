from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/', views.login, name='login'),
    url(r'^login/loading', views.login_validation, name='login_validation'),
]
