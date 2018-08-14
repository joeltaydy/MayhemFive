import traceback
from Module_TeamManagement.models import *

#-----------------------------------------------------------------------------#
#-------------------------- Utilities Function -------------------------------#
#-----------------------------------------------------------------------------#

'''
Populate relevant courses related to instructors/students from database
'''
def populateRelevantCourses(requests,instructorEmail=None,studentEmail=None):
    courseList = {}

    if instructorEmail != None:
        courseObject = Faculty.objects.get(email=instructorEmail).course_section.all()
        for course in courseObject:
            courseList[course.course_section_id] = course.course.course_title + " " + course.section_number

    elif studentEmail != None:
        classObject = Class.objects.all().filter(student=studentEmail).distinct()
        for individuaClass in classObject:
            course_section = individuaClass.course_section
            courseList[course_section.course_section_id] = course_section.course.course_title + " " + course_section.section_number

    requests.session['courseList'] = courseList
    return
