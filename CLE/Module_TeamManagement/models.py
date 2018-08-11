from django.db import models

class Course(models.Model):
    course_title = models.CharField(
        db_column='Course_Title',
        max_length=255,
        primary_key=True,
    )
    course_name = models.CharField(
        db_column='Course_Name',
        max_length=255,
    )
    course_description = models.TextField(
        db_column='Course_Description',
        null=True,
    ) 

    class Meta:
        managed = True
        db_table = 'Course'

class Student(models.Model):
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

    class Meta:
        managed = True
        db_table = 'Student'

class Course_Section(models.Model):
    course_section_id = models.CharField(
        db_column='Course_Section_ID',
        max_length=255,
        primary_key=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        db_column='Course',
    )
    section_number = models.CharField(
        db_column='Section_Number',
        max_length=2,
    )
    teaching_assistant = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        db_column='Teaching_Assistant',
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'Course_Section'
        unique_together = (('course','section_number'),('course', 'teaching_assistant'))

class Faculty(models.Model):
    email = models.EmailField(
        db_column='Faculty_Email',
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
    phone_number = models.CharField(
        db_column='Phone_Number',
        max_length=10,
        null=True,
    )
    telegram_username = models.CharField(
        db_column='Faculty_Telegram_Username',
        max_length=255,
        null=True,
    )
    course_section = models.ManyToManyField(
        Course_Section,
        db_column='Course_Section',
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'Faculty'

class Cloud_Learning_Tools(models.Model):
    id = models.AutoField(
        db_column='ID',
        primary_key=True,
    )
    type = models.CharField(
        db_column='Type',
        max_length=255,
    )
    website_link = models.TextField(
        db_column='Website_Link',
    )

    class Meta:
        managed = True
        db_table = 'Cloud_Learning_Tools'

class Class(models.Model):
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

    grades = models.CharField(
        db_column='Student_Grades',
        max_length=2,
        null=True,
        choices=GRADES_CHOICES,
    )
    score = models.IntegerField(
        db_column='Student_Score',
        null=True,
    )
    telegram_grouplink = models.TextField(
        db_column='Telegram_Grouplink',
        null=True,
    )
    telegram_channellink = models.TextField(
        db_column='Telegram_Channellink',
        null=True,
    )
    team_number = models.CharField(
        db_column='Team_Number',
        max_length=255,
        null=True,
    )
    clt_id = models.ForeignKey(
        Cloud_Learning_Tools,
        on_delete=models.CASCADE,
        db_column='CLT_ID',
        null=True,
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        db_column='Student',
    )
    course_section = models.ForeignKey(
        Course_Section,
        on_delete=models.CASCADE,
        db_column='Course_Section',
    )

    class Meta:
        managed = True
        db_table = 'Class'
        unique_together = (('clt_id','student','course_section'),)
