from django import forms
from Module_EventConfig.models import *


class EventsForm(forms.ModelForm):
    class Meta:
        model = Events_Log
        fields = ('events_date', 'events_name','events_type','events_team','events_status', )
        labels = {
            'events_date':'Date',
            'events_name':'Name',
            'events_type':'Type',
            'events_team':'Team',
            'events_status':'Status',
        }
