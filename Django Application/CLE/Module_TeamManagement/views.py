# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

def login(requests):
    return render(requests,"login.html",{})

def home(requests):
    return render(requests,"home.html",{})
