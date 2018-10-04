from django.contrib import admin
from django.urls import path, include
from Module_TeamManagement import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('Module_TeamManagement.urls','Module_TeamManagement'), namespace="TMmod")),
    path('', include(('Module_Account.urls','Module_Account'), namespace="Amod")),
    path('', include(('Module_DeploymentMonitoring.urls','Module_DeploymentMonitoring'), namespace="DMmod")),
    path('accounts/', include('allauth.urls')),

]
