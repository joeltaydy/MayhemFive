from django.shortcuts import render

def runUAT_Process(request):
    return render(requests,"Module_DeploymentMonitoring/Admin/<PAGE_NAME>.html",context)
