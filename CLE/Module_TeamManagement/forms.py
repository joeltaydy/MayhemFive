from django import forms

# class InstructorToolsForm(forms.Form):
#     tools = forms.ChoiceField(choices=[('Trailhead','Tableau','Kahoot')])

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=8)

class VerificationCodeForm(forms.Form):
    login_code = forms.CharField(max_length=6)
