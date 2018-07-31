from django.contrib import admin
from Module_Account import views
from django.urls import path

urlpatterns = [
    path('', views.login, name='login'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
]
