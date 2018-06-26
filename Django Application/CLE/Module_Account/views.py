# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages

# ------------------- Routing ---------------------#
def login(requests):
    return render(requests,"login.html",{})

# ------------------- Form parsing ---------------------#
def login_validation(request):
    from src import validate

    data = {}

    if "GET" == request.methoh:
        return render(request, "login.html", data)

    # if not GET, then proceed
    try:
        username = request.get("username", False)
        password = request.get("password", False)

        if username == "" or password == "":
            messages.error(request,"Please enter credentials")
            return HttpResponseRedirect(reverse("TMmod:login.html"))

        if validate.validate(username,password):
            messages.error(request,"Incorrect username or password")
            return HttpResponseRedirect(reverse("TMmod:login.html"))

    except Exception as e:
        return

    return HttpResponseRedirect(reverse("TMmod:studentHome.html"))
