# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from Module_Account.src import processLogin
import traceback

def login(requests):
    result = {}

    if requests.method == "GET":
        return render(requests, "login.html", result)

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
        return render(requests, "login.html", {"error" : str(e)})

    if result["status"] == "admin":
        return render(requests, "Instructor/instructorOverview.html", result)

    if result["first_time"]:
        return render(requests, "passwordMgmt.html", result)
    else:
        return redirect("/student/team/")

def passwordMgmt(requests):
    if requests.method == "GET":
        return redirect("/login/")

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

def logout(requests):
    return redirect("/login/")
