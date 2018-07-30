# from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from  django.http import HttpResponseRedirect
from django.conf import settings

class SocialAccountWhitelist(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email_address=sociallogin.account.extra_data["email"].split('@')[1]
        if not email_address == "smu.edu.sg":
            raise ImmediateHttpResponse(HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL,"non SMU account"))
