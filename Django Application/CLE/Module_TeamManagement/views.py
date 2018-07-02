# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from Module_TeamManagement.src import bootstrap
from Module_TeamManagement.models import Assigned_Team
import traceback

def home(requests): #student home page
    context = {}
    return render(requests,"Student/studentHome.html",context)

def instOverview(requests): #instructor overview page
    
    teams = Assigned_Team.objects.all().order_by('section')

    context = {"teamList" : teams}
    return render(requests,"Instructor/instructorOverview.html",context)

def studTeam(requests): # student team view page
    sectionNo = 'G2'
    teams = teams = Assigned_Team.objects.filter(section = sectionNo)

    context = {"teamList" : teams}
    return render(requests,"Student/studentTeam.html",context)


def uploadcsv(requests): # instructor bootstrap page
    if requests.method == "GET":
        return render(requests, "Instructor/uploadcsv.html", {})

    # If not GET, then proceed
    try:
        csv_file = requests.FILES.get("csv_file", False)

        # Checks if file is NOT xlsx
        if not csv_file.name.endswith('.xlsx'):
            error = "File is not CSV type"
            return render(requests, "Instructor/uploadcsv.html", {"error":error})

        # If file is xlsx then proceed with processing
        bootstrap.bootstrap(csv_file)

    except Exception as e:
        error = "Unable to upload file. " + repr(e)
        return render(requests, "Instructor/uploadcsv.html", {"error":error})

    return render(requests, "Instructor/uploadcsv.html", {"message": "Successful Upload"})
