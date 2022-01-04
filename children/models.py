from django_countries.fields import CountryField
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import (
    get_available_image_extensions,
    FileExtensionValidator,
)
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
import datetime
from django.shortcuts import get_object_or_404
from django.views.generic.edit import BaseDeleteView

from random import random
from tinymce.models import HTMLField
import os
import base64
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
# from users import models as cmodels
from general import models as gmodels
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from members import models as mmodels
import math



class General(models.Model):

    phone_number_1 = models.CharField(max_length=13, default ='', blank=True, )
    phone_number_1_handler = models.CharField(max_length=100, default ='', blank=True, )
    phone_number_2 = models.CharField(max_length=13, default ='', blank=True, )
    phone_number_2_handler = models.CharField(max_length=100, default ='', blank=True, )
    email_1 = models.CharField(max_length=100, default ='', blank=True, )
    email_1_handler = models.CharField(max_length=100, default ='', blank=True, )
    email_2 = models.CharField(max_length=100, default ='', blank=True, )
    email_2_handler = models.CharField(max_length=100, default ='', blank=True, )
    def __str__(self):
        return 'Children Administrators'
    class Meta:
        verbose_name ='Setting'

    def clean(self):
        """
        Throw ValidationError if you try to save more than one model instance
        See: http://stackoverflow.com/a/6436008
        """
        model = self.__class__
        if (model.objects.count() > 0 and
                self.id != model.objects.get().id):
            raise ValidationError(
                "Can only create 1 instance of %s." % model.__name__)



class LraMembersChildren(models.Model):
    child_id = models.AutoField(primary_key=True)
    c_surname = models.CharField(max_length=50, blank=True, null=True)
    c_firstname = models.CharField(max_length=50, blank=True, null=True)
    c_middlename = models.CharField(max_length=50, blank=True, null=True)
    c_gender = models.CharField(max_length=1, blank=True, null=True)
    c_date_of_birth = models.DateField(default=now,blank=True,editable=True)
    member_id = models.IntegerField(blank=True, null=True)
    c_phone = models.CharField(max_length=50, blank=True, null=True)
    c_email = models.CharField(max_length=50, blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    del_flg = models.CharField(max_length=1, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    created_on = models.DateField(auto_now=True)
    created_by = models.IntegerField(blank=True, null=True)
    last_modified_date = models.DateField(blank=True, null=True)
    last_modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lra_members_children'
        unique_together = (('c_surname', 'c_firstname', 'parent_id', 'del_flg'),)

    def __str__(self):
        return self.c_firstname +' ' + self.c_surname
