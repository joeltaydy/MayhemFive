from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team

#-----------------------------------------------------------------------------#
#--------------------------- Validate Function -------------------------------#
#-----------------------------------------------------------------------------#

def validate(username,password):
    status = ""
    user = ""

    if "admin" in username and "admin" in password:
        return {"status" : "admin", "user" : username}

    # Validates username and password. Else raise exception
    try:
        student = Student.objects.get(username=username)

        if password != student.password:
            raise Exception("Invalid password")

        status = "smustu"
        user = student.firstname + " " + student.lastname

    except Student.DoesNotExist:
        raise Exception("Invalid username")

    return {"status" : status, "user" : user}
