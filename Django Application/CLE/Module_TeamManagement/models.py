# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Instructor(models.Model):
    email = models.CharField(max_length=255, primary_key=True)
    username = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class Section(models.Model):
    section_number = models.CharField(max_length=255, primary_key=True)

class Team(models.Model):
    team_number = models.CharField(max_length=255)
    section_number = models.ForeignKey(Section, on_delete=models.CASCADE)
    # How to do composite primary key (section_number, team_number)?

class Section_Instructor(models.Model):
    section_number = models.ForeignKey(Section, on_delete=models.CASCADE)
    email = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    # How to do composite primary key (section_number, email)?

class Student(models.Model):
    email = models.CharField(max_length=255, primary_key=True)
    username = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    # How to do reference composite primary key from table Team(section_number, team_number)?
