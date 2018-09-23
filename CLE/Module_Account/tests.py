from django.test import TestCase
# Create your tests here.
from Module_Account.src import processLogin
from django.contrib.auth.models import User

class AccountModuleTest(TestCase):
    def test_login(self):
        a = processLogin.validate("admin","admin")
        self.assertTrue(isinstance(a, User))
        
        b = processLogin.validate("admin","admi2n")
        self.assertFalse(isinstance(b, User))