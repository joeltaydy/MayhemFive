from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team

#-----------------------------------------------------------------------------#
#--------------------------- Validate Function -------------------------------#
#-----------------------------------------------------------------------------#

def validate(username,password):
    status = ""
    user = ""
    first_time = False

    if "admin" in username and "admin" in password:
        return {"status" : "admin", "user" : username}

    # Validates username and password. Else raise exception
    try:
        student = Student.objects.get(username=username, password = password)
        status = "smustu"

        if password == "temp12345":
            first_time = True

    except :
        raise Exception("Invalid Username/Password")

    return {"status" : status, "user" : student, "first_time" : first_time}

def changePassword(oldPassword,newPassword,studObj):
    raise Exception("Incomplete")
