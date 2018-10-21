from django import forms
from Module_DeploymentMonitoring.models import *

class ServerForm_Add(forms.ModelForm):
    class Meta:
        model = Server_Details
        fields = ('IP_address', 'type', )
        labels = {
            'IP_address':'IP Address',
            'type':'Type',
        }

class ServerForm_Update(forms.ModelForm):
    class Meta:
        model = Server_Details
        fields = ('IP_address', 'type', )
        labels = {
            'IP_address':'IP Address',
            'type':'Type',
        }

class DeploymentForm(forms.ModelForm):
    class Meta:
        model = Deployment_Package
        fields = ('deploymentid', 'gitlink', )
        labels = {
            'deploymentid':'Deployment Package Name (Unique)',
            'gitlink':'Storage Link',
        }
