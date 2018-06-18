# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from  django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages


# ------------------- Routing ---------------------#
def login(requests):
    return render(requests,"login.html",{})

def home(requests):
    return render(requests,"home.html",{})

def uploadcsv(requests):
    return render(requests, "uploadcsv.html",{})


# ------------------- Form parsing ---------------------#
def upload_csv(request):
    from src import bootstrap
    data = {}
    if "GET" == request.method:
        return render(request, "TMmod/uploadcsv.html", data)
    # if not GET, then proceed
    try:
        csv_file = request.FILES.get("csv_file", False)
        if not csv_file.name.endswith('.xlsx'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse("TMmod:uploadcsv"))
        
        #if file is too large, return
        #if csv_file.multiple_chunks():
        #    messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
        #    return HttpResponseRedirect(reverse("TMmod:uploadcsv"))

       
        bootstrap.bootstrapData(csv_file)     
        
        
    except Exception as e:
        #logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
        messages.error(request,"Unable to upload file. "+repr(e))
        
 
    
    return HttpResponseRedirect(reverse("TMmod:uploadcsv"))