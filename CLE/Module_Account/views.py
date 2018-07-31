from django.shortcuts import render
from django.shortcuts import redirect
from Module_Account.src import processLogin
from  django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


# LOGIN VALIDATION -----------------------------------------------------------#
def login(requests):
    result = {}

    if requests.method == "GET":
        return render(requests, "Module_Account/login.html", result)
        return render(requests, "Registration/login.html", result)

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

        return render(requests, "Module_Account/login.html", {"error" : str(e)})

    if result["status"] == "admin":

        return render(requests, "Module_TeamManagement/Instructor/instructorOverview.html", result)
    else:
        #HttpResponseRedirect(('TMmod:home'))
        return render(requests, "Module_TeamManagement/Student/studentHome.html", result)



# LOGOUT ---------------------------------------------------------------------#
#@login_required(login_url='/')
def logout_view(requests):
    logout(requests)
    return redirect("/")
