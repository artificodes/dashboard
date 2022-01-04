from django.contrib.auth.hashers import make_password
from django.forms.models import model_to_dict
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
from random import choice, random
from tinymce.models import HTMLField
import os
import base64
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
# from users import models as cmodels
from general import models as gmodels
from django.utils.timezone import now




class LraMembersBiodata(models.Model):
    member_id = models.AutoField(primary_key=True)
    lra_membership_id = models.CharField(max_length=100, blank=True, default='', null=True)
    title = models.CharField(max_length=45, blank=True, default='', null=True)
    surname = models.CharField(max_length=50, blank=True, default='', null=True)
    firstname = models.CharField(max_length=50, blank=True, default='', null=True)
    middlename = models.CharField(max_length=50, blank=True, default='', null=True)
    maidenname = models.CharField(max_length=50, blank=True, default='', null=True)
    gender = models.CharField(max_length=1, blank=True, default='', null=True)
    marital_status = models.CharField(max_length=45, blank=True, default='', null=True)
    date_of_birth = models.DateField(blank=True,  auto_now=True)
    born_in_nigeria = models.IntegerField(default =0,blank=True)
    place_of_birth = models.CharField(max_length=45, blank=True, default='', null=True)
    home_town = models.CharField(max_length=45, blank=True, default='', null=True)
    address1 = models.CharField(max_length=200, blank=True, default='', null=True)
    address2 = models.CharField(max_length=200, blank=True, default='', null=True)
    country = models.CharField(max_length=45, blank=True, default='', null=True)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    lga = models.CharField(max_length=20, blank=True, default='', null=True)
    zip = models.CharField(max_length=20, blank=True, default='', null=True)
    nearest_b_stop = models.CharField(max_length=100, blank=True, default='', null=True)
    mobile1 = models.CharField(max_length=50, blank=True, default='', null=True)
    mobile2 = models.CharField(max_length=45, blank=True, default='', null=True)
    email = models.CharField(max_length=50, blank=True, default='', null=True)
    email2 = models.CharField(max_length=45, blank=True, default='', null=True)
    nationality = models.CharField(max_length=45, blank=True, default='', null=True)
    skype_id = models.CharField(max_length=20, blank=True, default='', null=True)
    unit_id = models.IntegerField(default =0,blank=True)
    position_in_dept = models.CharField(max_length=50, blank=True, default='', null=True)
    department_id = models.IntegerField(default =0,blank=True)
    department_status = models.CharField(max_length=2, blank=True, default='', null=True)
    cih_id = models.IntegerField(default =0,blank=True)
    chartered_flg = models.IntegerField(default =0,blank=True)
    affinity_group_id = models.IntegerField(blank=True, default=0, null=True)
    workforce_flg = models.IntegerField(default =0,blank=True)
    workforce_id = models.CharField(max_length=45,default='')
    mountain_id = models.IntegerField(default =0,blank=True)
    lra_govt_structure = models.CharField(max_length=100, blank=True, default='', null=True)
    date_of_spiritual_birth = models.DateField(blank=True,  auto_now=True)
    date_joined_lra = models.DateField(blank=True,  auto_now=True)
    edu_qual = models.CharField(max_length=100, blank=True, default='', null=True)
    prof_qual = models.CharField(max_length=100, blank=True, default='', null=True)
    employment_status = models.CharField(max_length=5, blank=True, default='', null=True)
    position = models.CharField(max_length=100, blank=True, default='', null=True)
    place_of_work = models.CharField(max_length=100, blank=True, default='', null=True)
    employer_address = models.CharField(max_length=100, blank=True, default='', null=True)
    employer_address2 = models.CharField(max_length=100, blank=True, default='', null=True)
    employer_telephone = models.CharField(max_length=100, blank=True, default='', null=True)
    employer_country = models.CharField(max_length=45, blank=True, default='', null=True)
    employer_state = models.IntegerField(blank=True, default='', null=True)
    employer_lga = models.IntegerField(blank=True, default='', null=True)
    industry_sector = models.CharField(max_length=100, blank=True, default='', null=True)
    sub_sector_code = models.CharField(max_length=45,default='')
    sports = models.CharField(max_length=200, blank=True, default='', null=True)
    other_sports = models.CharField(max_length=100, blank=True, default='', null=True)
    social_causes = models.CharField(max_length=200, blank=True, default='', null=True)
    entrep_interest = models.CharField(max_length=200, blank=True, default='', null=True)
    interest_sector = models.CharField(max_length=200, blank=True, default='', null=True)
    del_flg = models.CharField(max_length=1,default='')
    status = models.CharField(max_length=1,default='')
    created_on = models.DateTimeField(blank=True,  auto_now=True)
    created_by = models.IntegerField(default =0,blank=True)
    last_modified_date = models.DateTimeField(blank=True,  auto_now=True)
    last_modified_by = models.IntegerField(default =0,blank=True)
    last_session_id = models.CharField(max_length=100, blank=True, default='', null=True)
    row_id = models.IntegerField(blank=True, default='', null=True)
    source = models.CharField(max_length=45, blank=True, default='', null=True)
    upload_flg = models.IntegerField(blank=True, default='', null=True)
    cooperative = models.IntegerField(default =0,blank=True)
    advisory = models.IntegerField(default =0,blank=True)
    training = models.IntegerField(default =0,blank=True)
    profile_image_path = models.CharField(max_length=100, blank=True, default='', null=True)
    chartered_verified_flg = models.IntegerField(default =0,blank=True)
    first_timer = models.CharField(max_length=1, blank=True, default='', null=True)

    class Meta:
        managed = False
        db_table = 'lra_members_biodata'

    def __str__(self):
        return str(self.firstname) + " " +str(self.surname)



class CgccPrograms(models.Model):
    programme = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    no_of_days = models.IntegerField(blank=True, null=True)
    start_time = models.CharField(max_length=45, blank=True, null=True)
    end_time = models.CharField(max_length=45, blank=True, null=True)
    expected_attendance = models.IntegerField()
    frequency = models.CharField(max_length=1)
    frequency_iterations = models.IntegerField()
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField()
    last_modified_date = models.DateTimeField()
    last_modified_by = models.IntegerField()
    del_flg = models.CharField(max_length=1)
    status = models.CharField(max_length=1)
    approval_status = models.CharField(max_length=1)
    equipment_required = models.IntegerField()
    reminder = models.IntegerField(blank=True, null=True)
    reminder_unit = models.CharField(max_length=45, blank=True, null=True)
    venue_required = models.IntegerField()
    venue_id = models.IntegerField(blank=True, null=True)
    last_programme_date = models.DateField(blank=True, null=True)
    next_programme_date = models.DateField(blank=True, null=True)
    attendee_code = models.CharField(max_length=10, blank=True, null=True)
    total_registered = models.IntegerField(blank=True, null=True)
    approved_by = models.IntegerField(blank=True, null=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    no_of_services = models.IntegerField(blank=True, null=True)
    allow_overflow = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cgcc_programs'


    def __str__(self):
        return self.programme



class CgccProgram(models.Model):
    programme = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    no_of_days = models.IntegerField(blank=True, null=True)
    start_time = models.CharField(max_length=45, blank=True, null=True)
    end_time = models.CharField(max_length=45, blank=True, null=True)
    expected_attendance = models.IntegerField()
    frequency = models.CharField(max_length=1)
    frequency_iterations = models.IntegerField()
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField()
    last_modified_date = models.DateTimeField()
    last_modified_by = models.IntegerField()
    del_flg = models.CharField(max_length=1)
    status = models.CharField(max_length=1)
    approval_status = models.CharField(max_length=1)
    equipment_required = models.IntegerField()
    reminder = models.IntegerField(blank=True, null=True)
    reminder_unit = models.CharField(max_length=45, blank=True, null=True)
    venue_required = models.IntegerField()
    venue_id = models.IntegerField(blank=True, null=True)
    last_programme_date = models.DateField(blank=True, null=True)
    next_programme_date = models.DateField(blank=True, null=True)
    attendee_code = models.CharField(max_length=10, blank=True, null=True)
    total_registered = models.IntegerField(blank=True, null=True)
    approved_by = models.IntegerField(blank=True, null=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    no_of_services = models.IntegerField(blank=True, null=True)
    allow_overflow = models.IntegerField()


    def __str__(self):
        return self.programme

class CgccProgramsRegistration(models.Model):
    program_id = models.IntegerField()
    member_id = models.IntegerField()
    dependant_flg = models.IntegerField(blank=True, null=True)
    date_registered = models.DateTimeField()
    program_count = models.IntegerField()
    attendance = models.IntegerField()
    status = models.CharField(max_length=1)
    del_flg = models.CharField(max_length=45)
    created_by = models.IntegerField()
    last_modified_date = models.DateTimeField()
    last_modified_by = models.IntegerField()
    attendance_marked_by = models.IntegerField(blank=True, null=True)
    attendance_marked_date = models.DateTimeField(blank=True, null=True)
    service = models.IntegerField(blank=True, null=True)
    first_timer = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 'cgcc_programs_registration'




class Department(models.Model):
    name = models.CharField(max_length=100,blank=True,default='')

    def __str__(self):
        return self.name



class Source(models.Model):
    name = models.CharField(max_length=100,blank=True,default='')
    is_social = models.BooleanField(default=False, verbose_name='Is this a social platform')

    def __str__(self):
        return self.name



class ReportCategory(models.Model):
    name = models.CharField(max_length=100,blank=True,default='')
    def __str__(self):
        return self.name




class Report(models.Model):
    programid = models.IntegerField(default=0)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, default='',null=True)
    source = models.ForeignKey(Source,on_delete=models.CASCADE, default='',null=True)
    category = models.ForeignKey(ReportCategory,on_delete=models.CASCADE, default='',null=True)
    number = models.IntegerField(blank=True,default=0)
    formatted_number = models.CharField(blank=True,default='',max_length=100)
    title = models.CharField(max_length=100,blank=True,default='')
    description = HTMLField(blank=True,default='')
    is_incident = models.BooleanField(default=False)
    social_percentage = models.IntegerField(default=0,blank=True)
    physical_percentage = models.IntegerField(default=0,blank=True)
    def __str__(self):

        return self.category.name

    def save(self,*args,**kwargs):
        super(Report,self).save(*args, **kwargs) 

        all_reports = Report.objects.filter(programid=self.programid)
        if self.source.is_social:
            social_reports = list(filter(lambda x:x.source.is_social==True,all_reports))
            total_social_number = 0
            for report in social_reports:
                total_social_number += report.number
            self.social_percentage =(self.number*100) / total_social_number
        physical_reports = list(filter(lambda x:x.source.is_social!=True and str(x.category.name).lower() != 'offering' and x.is_incident == False,  all_reports))

        total_physical_number = 0
        if len(physical_reports):
            for report in physical_reports:
                total_physical_number += report.number

            self.physical_percentage =(self.number*100) / total_physical_number
        if str(self.category.name).lower() == 'offering':
            self.formatted_number = '₦{:,.2f}'.format(self.number)
       
        super(Report,self).save() 


class Incident(models.Model):
    programid = models.IntegerField(default=0)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, default='',null=True)
    title = models.CharField(max_length=100,blank=True,default='')
    description = HTMLField(blank=True,default='')

    def __str__(self):
        return self.title


class ProgramRecord(models.Model):
    program = models.ForeignKey(CgccProgram,on_delete=models.CASCADE,default=1,null= True)
    programid = models.IntegerField(default=0)
    incidents = models.ManyToManyField(Incident,default='',blank=True)
    reports = models.ManyToManyField(Report,default='',blank= True)
    total_attendance = models.IntegerField(blank=True,default=0)
    total_incidence = models.IntegerField(blank=True,default=0)

    def __str__(self):
        return str(self.program.programme)

    def save(self,*args,**kwargs):
        super(ProgramRecord,self).save(*args,**kwargs)
        total_attendance = 0
        total_incidence = self.incidents.all().count()

        for report in self.reports.all():
            total_attendance += report.number
        self.total_attendance = total_attendance
        self.total_incidence = total_incidence
        super(ProgramRecord,self).save()


class ApprovedUser(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE,default='',null=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100,default='',blank=True)
    last_name = models.CharField(max_length=100,default='',blank=True)
    phone_number = models.CharField(max_length=15,default='',blank=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,default='',null = True)
    report_category = models.CharField(max_length=50,default='',choices=(('attendance','attendance'),('incident','incident'),('offering','offering')))
    source_permission = models.ManyToManyField(Source,default='',blank=True)
    report_category_permission = models.ManyToManyField(ReportCategory,default='',blank=True)
    reports = models.ManyToManyField(Report,default='',blank=True)
    password = models.CharField(max_length=100,default='',blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


    def save(self,*args,**kwargs):
        super(ApprovedUser,self).save(*args,**kwargs)
        try:
            user = User.objects.get(email=self.email)
        except ObjectDoesNotExist:
            user = User.objects.create(email = self.email,username=self.email,password=make_password(self.password))
            user.refresh_from_db()
            user.is_active = True
        if self.is_staff:
            user.is_staff= True
        if self.is_superuser:
            user.is_superuser = True
        user.save()
        self.user= user
        self.password = ''

        super(ApprovedUser,self).save()

