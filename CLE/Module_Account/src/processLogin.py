from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team

#-----------------------------------------------------------------------------#
#--------------------------- Validate Function -------------------------------#
#-----------------------------------------------------------------------------#

def validate(username,password):
    status = ""
    user = ""

    if username == "admin" and password == "admin":
        return {"status" : "admin", "user" : username}

    # Validates username and password. Else raise exception
    try:
        student = Student.objects.get(username=username, password = password)
        status = "smustu"

    except :
        raise Exception("Invalid Username/Password")

    return {"status" : status, "user" : student}

def changePassword(oldPassword,newPassword,studObj):
    raise Exception("Incomplete")
