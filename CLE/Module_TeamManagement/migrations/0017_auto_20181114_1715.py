# Generated by Django 2.0.7 on 2018-11-14 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Module_TeamManagement', '0016_auto_20181111_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegram_chats',
            name='link',
            field=models.TextField(db_column='Link', null=True),
        ),
    ]
