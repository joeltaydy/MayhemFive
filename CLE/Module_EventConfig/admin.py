from django.contrib import admin
from Module_EventConfig.models import *
# Register your models here.


class EventAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('id','event_type', 'event_startTime', 'event_endTime', 'event_recovery', 'server_ip')
    # add filtering by date
    #list_filter = ('date',)
    # add search field 
    def server_ip(self,obj):
        return obj.server_details.IP_address


admin.site.register(Event_Details, EventAdmin)