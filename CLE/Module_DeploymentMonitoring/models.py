from django.db import models


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
        db_column='Instance_Name',
        max_length=255,
        null = True
    )
    state = models.CharField(
        db_column="Server_State",
        max_length = 255,
        null = True
    )

    class Meta:
        managed = True
        db_table = 'Server_Details'


class Image_Details(models.Model):
    imageId = models.CharField(
        db_column='Image_ID',
        max_length=255,
        primary_key=True,
    )
    imageName = models.CharField(
        db_column='Image_Name',
        max_length=255,
        null = True
    )
    sharedAccNum = models.TextField(
        db_column='List_of_shared_account_number',
        null = True
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

class AWS_Credentials(models.Model):
    account_number = models.CharField(
        db_column='AccountNumber',
        max_length=255,
        primary_key=True,
    )
    access_key = models.TextField(
        db_column='Access_Key',
        null= True
    )
    secret_access_key = models.TextField(
        db_column='Secret_Access_Key',
        null= True
    )
    serverDetails = models.ForeignKey(
        Server_Details,
        on_delete= models.CASCADE,
        db_column = 'Server_Details',
        null=True,
    )
    imageDetails = models.ForeignKey(
        Image_Details,
        on_delete= models.CASCADE,
        db_column = 'Image_Details',
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'AWS_Credentials'
