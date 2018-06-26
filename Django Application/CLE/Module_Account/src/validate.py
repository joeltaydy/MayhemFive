from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team

#-----------------------------------------------------------------------------#
#--------------------------- Validate Function -------------------------------#
#-----------------------------------------------------------------------------#

def validate(username,password):
    user = "admin"
    pwd = "admin"

    if user == username.strip() and pwd = password.strip():
        return True

    return False
