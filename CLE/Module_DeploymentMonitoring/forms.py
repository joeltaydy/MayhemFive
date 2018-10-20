from django import forms
from Module_DeploymentMonitoring.models import *

class ServerForm_Add(forms.ModelForm):
    class Meta:
        model = Server_Details
        fields = ('IP_address', 'instanceid', 'type', )
        labels = {
            'IP_address':'IP Address',
            'instanceid':'Instance ID',
            'type':'Type',
        }

class ServerForm_Update(forms.ModelForm):
    class Meta:
        model = Server_Details
        fields = ('IP_address', 'instanceid', 'instanceName', 'type', )
        labels = {
            'IP_address':'IP Address',
            'instanceid':'Instance ID',
            'instanceName':'Name',
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
