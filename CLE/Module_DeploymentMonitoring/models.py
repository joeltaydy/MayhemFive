from django.db import models

class Instance(models.Model):
    instance_id = models.CharField(
        db_column='Instance_ID',
        primary_key=True,
        max_length=255
    )
    public_ip = models.CharField(
        db_column='Public_IP',
        null=True,
        max_length=255
    )

    class Meta:
        managed = True
        db_table = 'Instance'

class Elastic_IPs(models.Model):
    allocation_id = models.CharField(
        db_column='Allocation_ID',
        primary_key=True,
        max_length=255
    )

    class Meta:
        managed = True
        db_table = 'Elastic_IPs'
