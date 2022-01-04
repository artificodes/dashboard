from allauth.account.forms import SignupForm
from django import forms
from children import models as chmodels
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm


# class DependantImage(forms.ModelForm):
#     class Meta:
#         model = chmodels.Dependant
#         fields = ('photo',)


# class AddDependant(forms.ModelForm):
#     class Meta:
#         model = chmodels.Dependant
#         fields = ('special_care',)


# class AddChild(forms.ModelForm):
#     class Meta:
#         model = chmodels.LraMembersChildren
#         fields = ('c_firstname','c_surname','c_date_of_birth','c_gender',)
