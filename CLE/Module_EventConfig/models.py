from django.db import models
from Module_DeploymentMonitoring.models import Server_Details

class Event_Details(models.Model):
    event_type = models.CharField(
        db_column='Event_Type',
        max_length=255,
    )
    event_startTime = models.CharField(
        db_column='Event_Start_Time',
        max_length=255,
    )
    event_endTime = models.CharField(
        db_column='Event_End_Time',
        max_length=255,
        null=True
    )
    event_recovery = models.CharField(
        db_column='Event_Recovery_Time',
        max_length=255,
        null=True
    )
    server_details = models.ForeignKey(
        Server_Details,
        on_delete= models.CASCADE,
        db_column='Server_Details',
        null=True,
    )
    class Meta:
        managed = True
        db_table = 'Event_Details'

class Events_Log(models.Model):
    events_id = models.AutoField(
        db_column='Events_ID',
        primary_key=True,
    )
    events_date = models.DateTimeField(
        db_column='Events_Date',
        max_length=255,
        null=True,
    )
    events_name = models.CharField(
        db_column='Events_Name',
        max_length=255,
        null=True,
    )
    events_type = models.CharField(
        db_column='Events_Type',
        max_length=255,
        null=True,
    )
    events_team = models.CharField(
        db_column='Events_Team',
        max_length=255,
        null=True,
    )
    events_status = models.CharField(
        db_column='Events_Status',
        max_length=255,
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'Events_Log'
