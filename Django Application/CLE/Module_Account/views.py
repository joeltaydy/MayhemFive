# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from Module_Account.src import processLogin
import traceback

# LOGIN VALIDATION -----------------------------------------------------------#
def login(requests):
    result = {}

    if requests.method == "GET":
<<<<<<< HEAD
        return render(requests, "Module_Account/login.html", result)
=======
        return render(requests, "Registration/login.html", result)
>>>>>>> 7de00fd3f1d2bdd250c828c550ea802a2d5ef083

    # If not GET, then proceed
    try:
        username = requests.POST.get("username")
        password = requests.POST.get("password")

        # Default login for testing purpose
        if(username == "admin" and password == "admin123"):
            return redirect('/home/')

        # Proceed to validating of username and password
        result = processLogin.validate(username,password)

    except Exception as e:
<<<<<<< HEAD
        return render(requests, "Module_Account/login.html", {"error" : str(e)})

    if result["status"] == "admin":
        return render(requests, "Module_TeamManagement/Instructor/instructorOverview.html", result)
    else:
        #HttpResponseRedirect(('TMmod:home'))
        return render(requests, "Module_TeamManagement/Student/studentHome.html", result)
=======
        return render(requests, "Registration/login.html", {"error" : str(e)})

    if result["status"] == "admin":
        return render(requests, "Instructor/instructorOverview.html", result)

    if result["first_time"]:
        return render(requests, "passwordMgmt.html", result)
    else:
        return redirect("/student/team/")

# PASSWORD RESET --- {for first time login} ----------------------------------#
def password_reset(requests):
    if requests.method == "GET":
        return redirect("/accounts/login/")

    try:
        student = requests.POST.get("login_details")
        oldPwd = requests.POST.get("old_password")
        newPwd = requests.POST.get("new_password")

        if student.password == oldPwd:
            # Change password for first time login
            processLogin.changePassword(oldPwd,newPwd,student)

        else:
            raise Exception("Old password deos not match. Please re-enter.")

    except Exception as e:
        return render(requests, "passwordMgmt.html", {"error" : str(e)})

    return redirect("/student/team/")
>>>>>>> 7de00fd3f1d2bdd250c828c550ea802a2d5ef083

# LOGOUT ---------------------------------------------------------------------#
def logout(requests):
    return redirect("/accounts/login/")
