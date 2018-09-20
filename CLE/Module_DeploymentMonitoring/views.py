from django.shortcuts import render

def run_UAT_Process(request):
    return render(requests,"Module_DeploymentMonitoring/Admin/<PAGE_NAME>.html",context)
