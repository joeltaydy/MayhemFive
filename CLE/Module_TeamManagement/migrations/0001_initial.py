# Generated by Django 2.0.7 on 2018-09-02 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grades', models.CharField(choices=[('A+', 'A+'), ('A', 'A'), ('A-', 'A-'), ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'), ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('D+', 'D+'), ('D', 'D'), ('D-', 'D-'), ('F', 'F')], db_column='Student_Grades', max_length=2, null=True)),
                ('score', models.IntegerField(db_column='Student_Score', null=True)),
                ('telegram_grouplink', models.TextField(db_column='Telegram_Grouplink', null=True)),
                ('telegram_channellink', models.TextField(db_column='Telegram_Channellink', null=True)),
                ('team_number', models.CharField(db_column='Team_Number', max_length=255, null=True)),
            ],
            options={
                'db_table': 'Class',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cloud_Learning_Tools',
            fields=[
                ('id', models.CharField(db_column='ID', max_length=255, primary_key=True, serialize=False)),
                ('type', models.CharField(db_column='Type', max_length=255)),
                ('website_link', models.TextField(db_column='Website_Link')),
            ],
            options={
                'db_table': 'Cloud_Learning_Tools',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_title', models.CharField(db_column='Course_Title', max_length=255, primary_key=True, serialize=False)),
                ('course_name', models.CharField(db_column='Course_Name', max_length=255)),
                ('course_description', models.TextField(db_column='Course_Description', null=True)),
            ],
            options={
                'db_table': 'Course',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Course_Section',
            fields=[
                ('course_section_id', models.CharField(db_column='Course_Section_ID', max_length=255, primary_key=True, serialize=False)),
                ('section_number', models.CharField(db_column='Section_Number', max_length=2)),
                ('learning_tools', models.TextField(db_column='Course_Section_Learning_Tools_List', null=True)),
                ('course', models.ForeignKey(db_column='Course', on_delete=django.db.models.deletion.CASCADE, to='Module_TeamManagement.Course')),
            ],
            options={
                'db_table': 'Course_Section',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('email', models.EmailField(db_column='Faculty_Email', max_length=254, primary_key=True, serialize=False)),
                ('username', models.CharField(db_column='Username', max_length=255)),
                ('firstname', models.CharField(db_column='Firstname', max_length=255)),
                ('lastname', models.CharField(db_column='Lastname', max_length=255)),
                ('phone_number', models.CharField(db_column='Phone_Number', max_length=255, null=True)),
                ('telegram_username', models.CharField(db_column='Faculty_Telegram_Username', max_length=255, null=True)),
                ('course_section', models.ManyToManyField(db_column='Course_Section', null=True, to='Module_TeamManagement.Course_Section')),
            ],
            options={
                'db_table': 'Faculty',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='School_Term',
            fields=[
                ('school_term_id', models.CharField(db_column='School_Term_ID', max_length=255, primary_key=True, serialize=False)),
                ('term', models.CharField(db_column='Term', max_length=255)),
                ('financial_year', models.CharField(db_column='Financial_Year', max_length=255)),
                ('start_date', models.DateField(db_column='Start_Date')),
                ('end_date', models.DateField(db_column='End_Date')),
            ],
            options={
                'db_table': 'School_Term',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('email', models.EmailField(db_column='Student_Email', max_length=254, primary_key=True, serialize=False)),
                ('username', models.CharField(db_column='Username', max_length=255)),
                ('firstname', models.CharField(db_column='Firstname', max_length=255)),
                ('lastname', models.CharField(db_column='Lastname', max_length=255)),
                ('telegram_username', models.CharField(db_column='Student_Telegram_Username', max_length=255, null=True)),
                ('loginCounts', models.IntegerField(db_column='Number of Logins', default=0)),
            ],
            options={
                'db_table': 'Student',
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='school_term',
            unique_together={('financial_year', 'term')},
        ),
        migrations.AddField(
            model_name='course_section',
            name='teaching_assistant',
            field=models.ForeignKey(db_column='Teaching_Assistant', null=True, on_delete=django.db.models.deletion.CASCADE, to='Module_TeamManagement.Student'),
        ),
        migrations.AddField(
            model_name='class',
            name='clt_id',
            field=models.ManyToManyField(db_column='CLT_ID', null=True, to='Module_TeamManagement.Cloud_Learning_Tools'),
        ),
        migrations.AddField(
            model_name='class',
            name='course_section',
            field=models.ForeignKey(db_column='Course_Section', on_delete=django.db.models.deletion.CASCADE, to='Module_TeamManagement.Course_Section'),
        ),
        migrations.AddField(
            model_name='class',
            name='school_term',
            field=models.ForeignKey(db_column='School_Term', on_delete=django.db.models.deletion.CASCADE, to='Module_TeamManagement.School_Term'),
        ),
        migrations.AddField(
            model_name='class',
            name='student',
            field=models.ForeignKey(db_column='Student', on_delete=django.db.models.deletion.CASCADE, to='Module_TeamManagement.Student'),
        ),
        migrations.AlterUniqueTogether(
            name='course_section',
            unique_together={('course', 'teaching_assistant'), ('course', 'section_number')},
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('student', 'course_section', 'school_term')},
        ),
    ]
