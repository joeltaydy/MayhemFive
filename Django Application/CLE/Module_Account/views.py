# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from Module_Account.src import validate
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
        result = validate.validate(username,password)

    except Exception as e:
        return render(requests, "login.html", {"error" : str(e)})

    if result["status"] == "admin":
        return render(requests, "Instructor/instructorOverview.html", result)
    else:
        #HttpResponseRedirect(('TMmod:home'))
        return render(requests, "Student/studentHome.html", result)

def logout(requests):
    return redirect('/login/')
