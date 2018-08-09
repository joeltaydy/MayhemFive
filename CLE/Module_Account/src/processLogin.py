from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User



#-----------------------------------------------------------------------------#
#--------------------------- Validate Function -------------------------------#
#-----------------------------------------------------------------------------#

def validate(username,password):

    login_valid = (settings.ADMIN_LOGIN == username)
    pwd_valid = (password == settings.ADMIN_PASSWORD)
   
    if login_valid and pwd_valid:
        try:
            user = User.objects.get(username=username)
        except:
            # Create a new user. There's no need to set a password
            # because only the password from settings.py is checked.
            user = User(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.save()
        return user
    return None



def changePassword(oldPassword,newPassword,studObj):
    raise Exception("Incomplete")
