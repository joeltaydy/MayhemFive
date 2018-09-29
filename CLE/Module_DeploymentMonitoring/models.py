from django.db import models
from Module_TeamManagement.models import Faculty

class AWS_Credentials(models.Model):
    account_number = models.CharField(
        db_column='AccountNumber',
        max_length=255,
        primary_key=True,
    )
    access_key = models.TextField(
        db_column='Access_Key',
    )
    secret_access_key = models.TextField(
        db_column='Secret_Access_Key',
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        db_column='Faculty',
    )

    class Meta:
        managed = True
        db_table = 'AWS_Credentials'

class Server_Details(models.Model):
    IP_address = models.CharField(
        db_column='IP_Address',
        max_length=255,
        primary_key=True,
    )
    instanceid = models.CharField(
        db_column='Instance_ID',
        max_length=255,
    )
    instanceName = models.CharField(
        db_column='Instance Name',
        max_length=255,
    )
    state = models.CharField(
        db_column="Server State",
        max_length = 255,
    )
    credentials = models.ForeignKey(
        AWS_Credentials,
        on_delete= models.CASCADE,
        db_column = 'AWS Credential linked'
    )

    class Meta:
        managed = True
        db_table = 'Server_Details'


class Image_Details(models.Model):
    imageid = models.CharField(
        db_column='Image_ID',
        max_length=255,
        primary_key=True,
    )
    imagename = models.CharField(
        db_column='Image Name',
        max_length=255,
    )
    sharedAccNum = models.TextField(
        db_column='List of shared account number',
    )

    class Meta:
        managed = True
        db_table = 'Image_Details'


class Deployment_Package(models.Model):
    deploymentid = models.CharField(
        db_column='Deployment ID',
        max_length=255,
        primary_key=True,
    )
    gitlink = models.CharField(
        db_column='Git Hub Link',
        max_length=255,
    )

    class Meta:
        managed = True
        db_table = 'Deployment_Package'
