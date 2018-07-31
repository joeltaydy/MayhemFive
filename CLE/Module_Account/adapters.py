# from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from  django.http import HttpResponseRedirect
from django.conf import settings
from django.dispatch import receiver
from django.contrib import messages

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from allauth.account.signals import user_signed_up


class SocialAccountWhitelist(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email_address=sociallogin.account.extra_data["email"].split('@')[1]
        messages.error(request, "Please use an SMU account")
        if not email_address == "smu.edu.sg":
            raise ImmediateHttpResponse(HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL))
