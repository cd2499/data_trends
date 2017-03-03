"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from .models import GetCar

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class GetCarForm(ModelForm):
    class Meta:
        model = GetCar
        fields = ['carmake', 'carmodel', 'caryear']




class CarSelectForm(forms.Form):
    make = forms.CharField(max_length=250)
    model = forms.CharField(max_length=250)
    year = forms.IntegerField(min_value=1990, max_value=2017)


class EdmundsCarSelectForm(forms.Form):
    make = forms.CharField(max_length=250)
    model = forms.CharField(max_length=250)
    year = forms.IntegerField(min_value=1990, max_value=2017)

