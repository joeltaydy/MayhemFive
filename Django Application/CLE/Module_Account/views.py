# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from Module_Account.src import validate
import traceback

def login(requests):
    if requests.method == "GET":
        return render(requests, "login.html", {})

    # If not GET, then proceed
    try:
        username = requests.POST.get("username")
        password = requests.POST.get("password")

        # Proceed to validating of username and password
        result = validate.validate(username,password)

    except Exception as e:
        return render(requests, "login.html", {"error" : str(e)})

    return render(requests, "login.html", result)
