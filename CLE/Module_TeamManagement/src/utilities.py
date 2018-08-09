import traceback
from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team, Teaching_Assistant

#-----------------------------------------------------------------------------#
#-------------------------- Utilities Function -------------------------------#
#-----------------------------------------------------------------------------#

def getAllSections():
    sections = Section.objects.all()

def getAllStudents(section_number=None):
    if section_number != None:
        return Assigned_Team.objects.all().filter(seciton=section_number)

    return Student.objects.all()

def getAllTeams(section_number=None):
    if section_number != None:
        assigned_teams = Assigned_Team.objects.all().filter(seciton=section_number).group
