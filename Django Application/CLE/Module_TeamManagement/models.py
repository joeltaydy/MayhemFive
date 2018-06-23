# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Instructor(models.Model):
    email = models.CharField(db_column='Email', max_length=255, primary_key=True)
    username = models.CharField(db_column='Username', max_length=255)
    firstname = models.CharField(db_column='Firstname', max_length=255)
    lastname = models.CharField(db_column='Lastname', max_length=255)
    password = models.CharField(db_column='Password', max_length=255)

    class Meta:
        managed = True
        db_table = 'Instructor'

class Section(models.Model):
    section_number = models.CharField(db_column='Section_Number', max_length=255, primary_key=True)

    class Meta:
        managed = True
        db_table = 'section'

class Team(models.Model):
    team_number = models.CharField(db_column='Team_Number', max_length=255)
    section_number = models.ForeignKey(Section, on_delete=models.CASCADE, db_column='Section_Number')

    class Meta:
        managed = True
        db_table = 'Team'
        unique_together = (('section_number','team_number'),)

class Section_Instructor(models.Model):
    section_number = models.ForeignKey(Section, on_delete=models.CASCADE, db_column='Section_Number')
    instructor_email = models.ForeignKey(Instructor, on_delete=models.CASCADE, db_column='Instructor_Email')

    class Meta:
        managed = True
        db_table = 'Section_Instructor'
        unique_together = (('section_number', 'instructor_email'),)

class Student(models.Model):
    email = models.CharField(max_length=255, primary_key=True)
    username = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
#    section_number = models.ForeignKey(Team, on_delete=models.CASCADE, db_column='Section_Number')
#    team_number = models.ForeignKey(Team, on_delete=models.CASCADE, db_column='Team_number')

    class Meta:
        managed = True
        db_table = 'Student'
