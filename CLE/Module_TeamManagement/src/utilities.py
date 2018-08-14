import traceback
from Module_TeamManagement.models import *

#-----------------------------------------------------------------------------#
#-------------------------- Utilities Function -------------------------------#
#-----------------------------------------------------------------------------#

'''
Populate relevant courses related to instructors/students from database
'''
def populateRelevantCourses(requests,instructorEmail=None,studentEmail=None):
    if instructorEmail != None:
        courseObject = Faculty.objects.get(email=instructorEmail).course_section.all()
    elif studentEmail != None:
        courseObject = Class.objects.filter(student=studentEmail).distinct()

    courseList = {}
    for course in courseObject:
        courseList[course.course_section_id] = course.course.course_title + " " + course.section_number

    requests.session['courseList'] = courseList
    return
