# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from Module_TeamManagement.src import bootstrap
import traceback

def home(requests):
    return render(requests,"studentHome.html",{})

def uploadcsv(requests):
    if requests.method == "GET":
        return render(requests, "uploadcsv.html", {})

    # If not GET, then proceed
    try:
        csv_file = requests.FILES.get("csv_file", False)

        # Checks if file is NOT xlsx
        if not csv_file.name.endswith('.xlsx'):
            messages.error(requests,'File is not CSV type')
            return HttpResponseRedirect("upload/csv/")

        # If file is xlsx then proceed with processing
        bootstrap.bootstrap(csv_file)

    except Exception as e:
        messages.error(requests,"Unable to upload file. " + repr(e))
        traceback.print_exc()

    return render(requests, "uploadcsv.html", {})
