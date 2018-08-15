# from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from allauth.exceptions import ImmediateHttpResponse
from  django.http import HttpResponseRedirect
from django.conf import settings
from django.dispatch import receiver
from django.contrib import messages
import re
from django.urls import reverse

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from allauth.account.signals import user_signed_up



class SocialAccountWhitelist(DefaultSocialAccountAdapter):

    def get_connect_redirect_url(self, request, socialaccount):
        assert request.user.is_authenticated

        path = "instructor/home/"
        return path


    # This method overwrites the child class to populate user log in in database
    '''
    def populate_user(self,
                      request,
                      sociallogin,
                      data):
        pass
    '''

    def pre_social_login(self, request, sociallogin):
        email_address=sociallogin.account.extra_data["email"].split('@')[1]
        messages.error(request, "Please use an SMU account")

        #use for team's test using any gmail account w/o numbers infront
        isInstructor = re.findall(r"(^[a-zA-Z.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",sociallogin.account.extra_data["email"])

        #uncomment below for staff email
        #isInstructor = re.findall(r"(^[a-zA-Z.]+@smu.edu.sg+$)",sociallogin.account.extra_data["email"])

        # Pretty much hard code the login redirect url as the overwriting method above does not seem to be work
        print(isInstructor)
        if isInstructor != [] :
            settings.LOGIN_REDIRECT_URL = "TMmod:instHome"


        elif not email_address == "smu.edu.sg":
            raise ImmediateHttpResponse(HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL))

        else:
            settings.LOGIN_REDIRECT_URL = "TMmod:home"
