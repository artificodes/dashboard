from allauth.account.forms import SignupForm
from django import forms
from members import models as gmodels
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm





# class addevent(forms.ModelForm):
#     title = forms.CharField(label='Title',initial='Title')

#     class Meta:
#         model = gmodels.Event
#         fields = ('title','thumbnail',)

# class addeventday(forms.ModelForm):
#     title = forms.CharField(label='Title',initial='Title')

#     class Meta:
#         model = gmodels.EventDay
#         fields = ('title','thumbnail',)

# class editevent(forms.ModelForm):
#     title = forms.CharField(label='Title',initial='Title')

#     class Meta:
#         model = gmodels.HostedEvent
#         fields = ('title','thumbnail',)

# class createeventticket(forms.ModelForm):
#     name = forms.CharField(label='Title',initial='Title')

#     class Meta:
#         model = gmodels.EventTicket
#         fields = ('name','price','attendance_limit','sections','tables_per_section','chairs_per_table')

# class createeventarrangement(forms.ModelForm):
#     name = forms.CharField(label='Title',initial='Title')

#     class Meta:
#         model = gmodels.Arrangement
#         fields = ('name','sections','chairs_per_table')