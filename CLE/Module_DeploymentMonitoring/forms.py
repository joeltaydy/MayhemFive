from django import forms
from Module_DeploymentMonitoring.models import *

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server_Details
        fields = ('IP_address', 'instanceid', 'instanceName', 'state', )

class DeploymentForm(forms.ModelForm):
    class Meta:
        model = Deployment_Package
        fields = ('deploymentid', 'gitlink', )
