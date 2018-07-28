from django.db import models

class Section(models.Model):
    section_number = models.CharField(
        db_column='Section_Number',
        max_length=2,
        primary_key=True,
    )

    class Meta:
        managed = True
        db_table = 'Section'

class Student(models.Model):
    GRADES_CHOICES = (
        ('A+','A+'),
        ('A','A'),
        ('A-','A-'),
        ('B+','B+'),
        ('B','B'),
        ('B-','B-'),
        ('C+','C+'),
        ('C','C'),
        ('C-','C-'),
        ('D+','D+'),
        ('D','D'),
        ('D-','D-'),
        ('F','F'),
    )

    email = models.EmailField(
        db_column='Student_Email',
        primary_key=True,
    )
    username = models.CharField(
        db_column='Username',
        max_length=255,
    )
    firstname = models.CharField(
        db_column='Firstname',
        max_length=255,
    )
    lastname = models.CharField(
        db_column='Lastname',
        max_length=255,
    )
    telegram_username = models.CharField(
        db_column='Student_Telegram_Username',
        max_length=255,
        null=True,
    )
    grades = models.CharField(
        db_column='Student_Grades',
        max_length=2,
        null=True,
        choices=GRADES_CHOICES,
    )
    marks = models.IntegerField(
        db_column='Student_Marks',
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'Student'

class Instructor(models.Model):
    email = models.EmailField(
        db_column='Instructor_Email',
        primary_key=True,
    )
    username = models.CharField(
        db_column='Username',
        max_length=255,
    )
    firstname = models.CharField(
        db_column='Firstname',
        max_length=255,
    )
    lastname = models.CharField(
        db_column='Lastname',
        max_length=255,
    )
    section = models.ManyToManyField(
        Section,
        db_column='Section',
    )
    telegram_username = models.CharField(
        db_column='Instructor_Telegram_Username',
        max_length=255,
        null=True,
    )
    phone_number = models.IntegerField(
        db_column='Phone_Number',
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'Instructor'

class Assigned_Team(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        db_column='Student',
        primary_key=True
    )
    team_number = models.CharField(
        db_column='Team_Number',
        max_length=2,
        default='T0'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        db_column='Section',
        default='G0'
    )

    class Meta:
        managed = True
        db_table = 'Assigned_Team'

class Teaching_Assistant(models.Model):
    email = models.EmailField(
        db_column='Teaching_Assistant_Email',
        primary_key=True,
    )
    username = models.CharField(
        db_column='Username',
        max_length=255,
    )
    firstname = models.CharField(
        db_column='Firstname',
        max_length=255,
    )
    lastname = models.CharField(
        db_column='Lastname',
        max_length=255,
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        db_column='Section',
        default='G0'
    )
    telegram_username = models.CharField(
        db_column='TA_Telegram_Username',
        max_length=255,
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'Teaching_Assistant'
