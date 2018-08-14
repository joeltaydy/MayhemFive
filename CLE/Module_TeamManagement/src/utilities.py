import traceback
from Module_TeamManagement.models import *

#-----------------------------------------------------------------------------#
#-------------------------- Utilities Function -------------------------------#
#-----------------------------------------------------------------------------#

'''
Populate relevant courses related to instructors/students from database
'''
def populateRelevantCourses(requests, instructorEmail=None,studentEmail=None ):
    if instructorEmail != None:
        courseObject = Faculty.objects.get(email=instructorEmail).course_section.all() #to filter the courses
    elif studentEmail != None: 
        courseObject = Class.objects.filter(student=studentEmail).distinct()
    courseList = []
    for course in courseObject:
        courseList.append(course.course_section_id)
    requests.session['courseList'] = courseList
    return

def getAllSections():
    sections = Section.objects.all()

def getAllStudents(section_number=None):
    if section_number != None:
        return Assigned_Team.objects.all().filter(section=section_number)

    return Student.objects.all()

def getAllTeams(section_number=None):
    if section_number != None:
        assigned_teams = Assigned_Team.objects.all().filter(section=section_number).group
