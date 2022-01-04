from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.db.models.lookups import Regex
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from general import forms as gforms
from django.core.exceptions import ObjectDoesNotExist
from general import models as gmodels
from random import random
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from general.tokens import account_activation_token
import math
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
import datetime
import os
import base64
from django.forms import ModelForm
from django.conf import settings
from django import forms
import datetime
from allauth.account.views import AjaxCapableProcessFormViewMixin
from django.contrib.auth.decorators import login_required
from random import random
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.template import loader
from django.http import JsonResponse
from django.urls import reverse_lazy
from allauth.account import forms as allauthforms
from django.core.mail import send_mail
from members import models as mmodels
from members import forms as uforms
allObject = {}


def inherit(request, *args, **kwargs):
    allObject = {}

    current_user = mmodels.ApprovedUser.objects.get(user=User.objects.get(email=request.user.email),)
    try:
        settings = list(gmodels.General.objects.all())[0]
    except IndexError:
        settings = []
    allObject['settings'] = settings
    allObject['server_timestamp'] = math.floor(datetime.datetime.now().timestamp())
    allObject['member'] = current_user
    return allObject


@login_required
def home(request, *args, **kwargs):
    
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/actions.html'
    return render(request,template_name,allObject)



def record_incidence(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']

    if request.method == 'POST':
        programid = int(request.POST.copy().get('program'))
        description = str(request.POST.copy().get('description'))        
        categoryname = str(request.POST.copy().get('category'))        
        departmentname = str(request.POST.copy().get('department'))
        title = str(request.POST.copy().get('title'))
        category = mmodels.ReportCategory.objects.get(name=categoryname)
        program = mmodels.CgccProgram.objects.get(pk=programid)
        department = mmodels.Department.objects.get(name=departmentname)
        incident = mmodels.Report.objects.create(programid = program.pk,category = category, is_incident=True, title=title, department=department,description=description)
        try:
            programrecord = mmodels.ProgramRecord.objects.get(program=program,)
        except ObjectDoesNotExist:
            programrecord = mmodels.ProgramRecord.objects.create(program=program,)

        programrecord.refresh_from_db()
        programrecord.reports.add(incident)
        programrecord.save()
        allObject['message'] = '<span class="text-primary uk-text-bold h1">Incidence Recorded </span>'
        message_template = 'general/success.html'
        global message
        message = loader.render_to_string(message_template,allObject,request)

        output_data = {
        'modal_message': message,
                        }
        return JsonResponse(output_data) 
    else:
        category = mmodels.ReportCategory.objects.get(name='incident')
        allObject['category'] = category
        departments = mmodels.Department.objects.all()
        programs = list(mmodels.CgccProgram.objects.filter(start_date__lte=datetime.datetime.now()))
        programs.sort(key=lambda x:x.start_date,reverse=True)
        allObject['departments'] = departments
        allObject['programs'] = programs
        content_template = 'members/incident_form.html'
        content = loader.render_to_string(content_template,allObject,request)
        output_data = {
        'modal_message': content,
                        }
        return JsonResponse(output_data) 



def record_attendance(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']

    if request.method == 'POST':
        programid = int(request.POST.copy().get('program'))
        platformid = int(request.POST.copy().get('source'))        
        categoryid = int(request.POST.copy().get('category'))
        departmentid = int(request.POST.copy().get('department'))
        number = int(request.POST.copy().get('number'))
        program = mmodels.CgccProgram.objects.get(pk=programid)
        source = mmodels.Source.objects.get(pk=platformid)
        category = mmodels.ReportCategory.objects.get(pk=categoryid)
        department = mmodels.Department.objects.get(pk=departmentid)
        report = mmodels.Report.objects.create(programid = program.pk,source=source,category=category,department=department,number=number)
        try:
            programrecord = mmodels.ProgramRecord.objects.get(program=program,)
        except ObjectDoesNotExist:
            programrecord = mmodels.ProgramRecord.objects.create(program=program,)

        programrecord.refresh_from_db()
        programrecord.reports.add(report)
        programrecord.save()
        member.reports.add(report)
        allObject['message'] = '<span class="text-primary uk-text-bold h1">Attendance Recorded </span>'
        message_template = 'general/success.html'
        global message
        message = loader.render_to_string(message_template,allObject,request)

        output_data = {
        'modal_message': message,
                        }
        return JsonResponse(output_data) 
    else:
        departments = mmodels.Department.objects.all()
        categorys = mmodels.ReportCategory.objects.all()
        source = mmodels.Source.objects.all()
        programs = list(mmodels.CgccProgram.objects.filter(start_date__lte=datetime.datetime.now()))
        programs.sort(key=lambda x:x.start_date,reverse=True)
        allObject['departments'] = departments
        allObject['source'] = source
        allObject['programs'] = programs
        allObject['categorys'] = categorys
        content_template = 'members/attendance_form.html'
        content = loader.render_to_string(content_template,allObject,request)
        output_data = {
        'modal_message': content,
                        }
        return JsonResponse(output_data) 



@login_required
def records(request, *args, **kwargs):
    if request.user.is_superuser:
        allObject = inherit(request, *args, **kwargs)
        for program in list(mmodels.CgccPrograms.objects.values()):
            try:
                newprogram = mmodels.CgccProgram.objects.get( id= program['id'])
            except ObjectDoesNotExist:
                newprogram = mmodels.CgccProgram.objects.create(**program)

        recorded = list(mmodels.ProgramRecord.objects.all())
        recorded.sort(key=lambda x:x.program.start_date,reverse=True)

        allObject['records'] = recorded
        template_name = 'members/records.html'
        return render(request,template_name,allObject)
    else:
        auth.logout(request)
        return redirect('home')



@login_required
def record(request,pk=None, *args, **kwargs):
    
    allObject = inherit(request, *args, **kwargs)
    recorded = mmodels.ProgramRecord.objects.get(pk=pk)
    program = recorded.program
    allObject['record'] = recorded
    allObject['program'] = program
    socialmediaplatforms = []
    socialmediatotal = 0
    for report in recorded.reports.all():
        report.save()
        if report.source.is_social:
            socialmediatotal+=report.number
            socialmediaplatforms.append(report)
    allObject['socialmediaplatforms'] = socialmediaplatforms
    allObject['socialmediatotal'] = socialmediatotal

    physicalcategories = []
    physicalcategoriestotal = 0
    for report in recorded.reports.all():
        report.save()
        if not report.source.is_social and str(report.category.name).lower() != 'offering' and not report.is_incident:
            physicalcategoriestotal+=report.number
            physicalcategories.append(report)
    allObject['physicalcategories'] = physicalcategories
    allObject['physicalcategoriestotal'] = physicalcategoriestotal
    content_template = 'members/record.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def incidence(request,pk=None, *args, **kwargs):
    
    allObject = inherit(request, *args, **kwargs)
    recorded_incidence = mmodels.Report.objects.get(pk=pk,is_incident=True)
    program = mmodels.CgccProgram.objects.get(pk=recorded_incidence.programid)

    allObject['incidence'] = recorded_incidence
    allObject['program'] = program
    content_template = 'members/incidence.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'modal_message': content,
                    }
    return JsonResponse(output_data) 



@login_required
def confirmemailpage(request,updated=False, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/email_confirmation_page.html'
    return render(request,template_name,allObject)
    return JsonResponse(output_data)  


@login_required
def checkmemberstatus(member):
    if not member.email_confirmed:
            return redirect('member_confirm_email_page')
    else:
        return True



def arrangeattendee(hostedevent,registration):
    if hostedevent.one_time_ticketing or hostedevent.one_time_arrangement:
        previous_registrations = mmodels.Registration.objects.filter(attendee=registration.attendee,eventid=hostedevent.eventid,)
        for registration in previous_registrations:
            if registration.seat_number != '':
                seat_number=registration.seat_number
                return seat_number 
    if hostedevent.one_time_arrangement:
        canregister = False
        if hostedevent.verification_steps == '0':
            for arrangement in hostedevent.arrangements.all():
                if not arrangement.full:
                    canregister = True
                    arrangement.registrations.add(registration)
                    arrangement.save()
                    # hostedevent.attendees.add(member)
                    hostedevent.save()
                    hostedevent.refresh_from_db()
                    registration.arrangementid = arrangement.arrangementid
                    registration.save()
                    if hostedevent.one_day:
                            seat_number=arrangement.initials+str(arrangement.registrations.count())
                            registration.seat_number=seat_number
                            registration.save()
                    elif arrangement.day:
                        eventday = chmodels.EventDay.objects.get(dayid=arrangement.dayid,eventid=hostedevent.eventid,hostedeventid=hostedeventid,)
                        if eventday.arrange:
                            seat_number=arrangement.initials+str(arrangement.registrations.count())
                            registration.seat_number=seat_number
                            registration.day= True
                            registration.dayid= arrangement.dayid
                            registration.save()
                    break
                else:
                    return 'No space'


@login_required
def checkparent(member):
    if member.has_dependants:
        return True
    
    return False


@login_required
def membersearch(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    template_name = 'members/member_summary.html'
    if request.method == 'POST':
        identifier = request.POST.copy().get('identifier')
        try:
            member = mmodels.LraMembersBiodata.objects.get(mobile1=identifier)
        except ObjectDoesNotExist:
            try:
                member = mmodels.LraMembersBiodata.objects.get(email=identifier)            
            except ObjectDoesNotExist:
                allObject['error'] = 'Member not found'
                allObject['searchedmember'] = False
                message = loader.render_to_string(template_name,allObject,request)        
                output_data={
                        'message':message,
                        'verified':False,
                                }
                return JsonResponse(output_data)
        allObject['searchedmember'] = member
        message = loader.render_to_string(template_name,allObject,request)        
        output_data={
                'message':message,
                        }
        return JsonResponse(output_data)


@login_required
def eventtab(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    template_name = 'members/events.html'
    upcomingevents =  list(mmodels.HostedEvent.objects.filter(
        end_date_time__gte = datetime.datetime.today().date(),open_to='adults'))
    upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
    parent = checkparent(member)
    if parent:
        childrenevents =  list(mmodels.HostedEvent.objects.filter(end_date_time__gte = datetime.datetime.now(),open_to='children'))
        upcomingevents.extend(childrenevents)
    allObject['upcomingevents'] =upcomingevents
    registrations = []
    for upcomingevent in upcomingevents:
        for registration in upcomingevent.registrations.all():
            if registration.attendee == member:
                registrations.append(registration)

    allObject['registrations'] = registrations
    events = list(mmodels.Event.objects.all())
    events.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['events'] =events 
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'content':content,
                    }
    return JsonResponse(output_data) 



@login_required
def hometab(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/home.html'
    member = allObject['member']
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'content':content,
                    }
    return JsonResponse(output_data) 


def registerattendee(allObject,hostedevent):
    member = allObject['member']
    if hostedevent.one_day:
        registration_id = hostedevent.initials+'00'+str(hostedevent.registrations.count()+1)+'-'+str(round(random()*1234567890))
        registration = mmodels.Registration.objects.create(registrationid=registration_id[0:8],attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
        hostedevent.registrations.add(registration)        
        if hostedevent.one_time_arrangement:
            if arrangeattendee(hostedevent,registration) == 'No space':
                registration.delete()
                message = 'Sorry, there is no more space for registration'
                output_data = {
                        'modal_message':message,
                                }
                return JsonResponse(output_data)
        updateeventstatus(hostedevent)
        allObject['hostedevent']=hostedevent
        allObject['message'] = "Congratulations! You have registered for " + hostedevent.title 
        upcomingevents =  list(mmodels.HostedEvent.objects.filter(
        end_date_time__gte = datetime.datetime.today().date(),open_to='adults'))
        upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
        allObject['upcomingevents'] =upcomingevents
        registrations = []
        for upcomingevent in upcomingevents:
            for registration in upcomingevent.registrations.all():
                if registration.attendee == member:
                    registrations.append(registration)
        allObject['registrations'] = registrations
        registration.refresh_from_db()     
        return registration
    return {'eventtitle':hostedevent.title,'registered':False}



@login_required
def dashboard(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/dashboard.html'
    member = allObject['member']
    memberstatus = checkmemberstatus(member)
    if type(memberstatus) == bool:
        events = mmodels.HostedEvent.objects.all()
        # thisevent= list(events)
        # thishostedevent.sort(key = lambda x:x.date_time_added,reverse=True)
        # thisevent[0].thumbnail = thisevent[3].thumbnail
        # thisevent[0].save()
        upcomingevents =  list(mmodels.HostedEvent.objects.filter(start_date_time__gt = datetime.datetime.now()))

        upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)

        allObject['upcomingevents'] =upcomingevents
        allarticles = mmodels.Article.objects.all()
        articles = []
        notifications = []
        for article in allarticles:
            if member in article.read.all():
                pass
            else:
                notifications.append(article)
        allannouncements = mmodels.Announcement.objects.all()
        announcements = []
        for announcement in allannouncements:
            if member in announcement.read.all():
                pass
            else:
                notifications.append(announcement)
        unreadnotifications = False
        if notifications:
            unreadnotifications = True
        notifications.sort(key=lambda x:x.date_time_added,reverse=True)
        allObject['notifications'] = notifications
        return render(request,template_name,allObject)
    else:
        return memberstatus



@login_required
def myevents(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/my_events.html'
    member = allObject['member']
    events = list(mmodels.Event.objects.filter())
    events.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['myevents'] =events
    return render(request,template_name,allObject)

@login_required
def updateprofileform(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/update_profile.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'modal_content':content,
            'header':'Profile Update',
            'message':'Kindly update your profile to access all features'
                    }
    return JsonResponse(output_data)  

from qr_code.qrcode.utils import QRCodeOptions

@login_required
def eventqrcode(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    input_data = str(hostedevent.hostedeventid)
    template_name = 'members/event_qrcode.html'
    allObject['qrtext']=hostedevent.eventid
    allObject['qrc_options'] =QRCodeOptions(hostedevent.eventid,size='18', border=8, error_correction='L',image_format='png', )
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'modal_content':content,
            'heading':hostedevent.title,
                    }
    return JsonResponse(output_data)  


@login_required
def memberidentity(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    memberid = member.memberid
    qrtext= memberid+'-'+str(datetime.datetime.now().timestamp())
    # +3600000.0 
    allObject['qrtext'] = qrtext
    template_name = 'members/member_identity.html'
    allObject['qrc_options'] =QRCodeOptions(qrtext,custom_text=qrtext, size='18', border=8, error_correction='L',image_format='png')
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'full_modal':content,
            
                    }
    return JsonResponse(output_data)  



@login_required
def attendeeqrcode(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    member = allObject['member']      
    registration = mmodels.Registration.objects.get(eventid=hostedevent.eventid,attendee=member)
    allObject['hostedevent'] = hostedevent
    input_data = str(hostedevent.eventid)
    template_name = 'members/event_qrcode.html'
    context = dict(
            qrc_options= QRCodeOptions(registration.registrationid,size='18', border=8, error_correction='L',image_format='png', ),
        )
    content = loader.render_to_string(template_name,context,request)
    output_data = {
            'modal_content':content,
            'header':hostedevent.title,
                    }
    return JsonResponse(output_data)  

def canattend(hostedevent,member):
    if hostedevent.open_to == 'adults':
        return True


@login_required
def attendeeqrcverification(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    qrcodeid = request.GET.get('eventid')
    try:

        event = mmodels.Event.objects.get(eventid=qrcodeid)
        member = allObject['member']

        for hostedevent in event.hosted_events.all():

            if canattend(hostedevent,member):
                if hostedevent.start_date_time.date() == datetime.datetime.today().date() and hostedevent.end_date_time.date() >= datetime.datetime.now().date() and hostedevent.end_date_time.time() >= datetime.datetime.now().time():
                    hostedevent = hostedevent
                    member = allObject['member']      
                    allObject['hostedevent'] = hostedevent
                    if hostedevent.one_day:
                        try:
                            registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
                            if hostedevent.verification_steps != '2':
                                registration.verified = True
                                registration.completed = True
                                registration.status = 'accredited'
                                registration.accredited_by ='qrcode'
                                registration.save()
                            else:
                                registration.verified = True
                                registration.save()          
                            if hostedevent.one_time_arrangement:
                                if arrangeattendee(hostedevent,registration) == 'No space':
                                    registration.delete()
                                    message = 'Sorry, there is no more space for registration'
                                    output_data = {
                                            'modal_message':message,
                                                    }
                                    return JsonResponse(output_data)            
                            upcomingevents =  list(mmodels.HostedEvent.objects.filter(
                            end_date_time__gte = datetime.datetime.today().date(),open_to='adults'))
                            upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
                            allObject['upcomingevents'] =upcomingevents
                            registrations = []
                            for upcomingevent in upcomingevents:
                                for registration in upcomingevent.registrations.all():
                                    if registration.attendee == member:
                                        registrations.append(registration)
                            allObject['registrations'] = registrations
                            template_name = 'members/success.html'
                            allObject['message'] = "Welcome " + hostedevent.title 
                            if registration.seat_number != '':
                                seatnumber= registration.seat_number
                                allObject['message'] = "Welcome to " + hostedevent.title +"<br> <span class='h2 text-darker uk-text-bold'> SEAT ID:</span> <span class='h2 uk-text-bold text-yellow'>"+seatnumber+'</span>'
                            message = loader.render_to_string(template_name,allObject,request)
                            updatecontenttemplate = 'members/upcoming_events.html'
                            updatecontent = loader.render_to_string(updatecontenttemplate,allObject,request)
                            output_data = {
                                    'heading':message,
                                    'modal_message':message,
                                    'updatecontent':updatecontent
                                            }
                            return JsonResponse(output_data)
                        except ObjectDoesNotExist:
                            allObject['hostedevent'] = hostedevent
                            registration = registerattendee()
                            if hostedevent.verification_steps != '2':
                                registration.verified = True
                                registration.completed = True
                                registration.status = 'accredited'
                                registration.accredited_by ='qrcode'
                                registration.save()
                            else:
                                registration.verified = True
                                registration.save()
                            if arrangeattendee(hostedevent,registration) == 'No space':
                                registration.delete()
                                message = 'Sorry, there is no more space for registration'
                                output_data = {
                                        'modal_message':message,
                                                }
                                return JsonResponse(output_data)
                            registration.refresh_from_db()
                            upcomingevents =  list(mmodels.HostedEvent.objects.filter(
                            end_date_time__gte = datetime.datetime.today().date(),open_to='adults'))
                            upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
                            allObject['upcomingevents'] =upcomingevents
                            registrations = []
                            for upcomingevent in upcomingevents:
                                for registration in upcomingevent.registrations.all():
                                    if registration.attendee == member:
                                        registrations.append(registration)
                            allObject['registrations'] = registrations
                            template_name = 'members/success.html'
                            allObject['message'] = "Welcome to " + hostedevent.title 
                            if registration.seat_number != '':
                                seatnumber= registration.seat_number
                                allObject['message'] = "Welcome to " + hostedevent.title +"<br> <span class='h2 text-darker uk-text-bold'> SEAT ID:</span> <span class='h2 uk-text-bold text-yellow'>"+seatnumber+'</span>'
                            message = loader.render_to_string(template_name,allObject,request)
                            updatecontenttemplate = 'members/upcoming_events.html'
                            updatecontent = loader.render_to_string(updatecontenttemplate,allObject,request)
                            output_data = {
                                    'heading':message,
                                    'modal_message':message,
                                    'updatecontent':updatecontent
                                            }
                            return JsonResponse(output_data)
                
                    elif hostedevent.days.count() > 0:
                        for eventday in hostedevent.days.all():
                            if qrcodeid == hostedevent.hostedeventid+eventday.dayid:
                                if eventday.start_date_time.date == datetime.datetime.now().date:
                                    registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=eventday.dayid)
                                    registration.verified = True
                                    if hostedevent.verification_steps != '2':
                                        registration.completed = True
                                    registration.save()
                                    if eventday.ticket_required and eventday.arrange:
                                        for eventticket in eventday.tickets.all():
                                            for ticketregistration in eventticket.registrations.all():
                                                if ticketregistration==registration:
                                                    ticket = eventticket
                                                    sections = ticket.sections
                                                    tables_per_section = ticket.tables_per_section
                                                    chairs_per_table = ticket.chairs_per_table
                                                    assigned_chairs = 0
                                                    total_chairs = sections*tables_per_section*chairs_per_table
                                                    seat_number =0
                                                    # section_percent = 100//sections
                                                    if tables_per_section==0:
                                                        chairs_percent = 100//(1 * chairs_per_table)
                                                    else:
                                                        chairs_percent = 100//(tables_per_section * chairs_per_table)
                                                    for registration in ticket.registrations.all():
                                                        if registration.verified:
                                                            assigned_chairs +=1
                                                    if assigned_chairs == total_chairs:
                                                        pass           
                                                    else:
                                                        if tables_per_section==0:
                                                            current_table=''
                                                        else:
                                                            current_table ='T'+str(math.ceil(assigned_chairs%chairs_per_table))
                                                        current_chair =(assigned_chairs%chairs_per_table)
                                                        if sections ==0:
                                                            current_section=''
                                                        else:
                                                            current_section ='S'+str(math.ceil(chairs_percent*assigned_chairs/100))

                                                        seat_number=ticket.name[0]+str(current_section)+str(current_table)+'C'+str(current_chair)
                                                        registration.seat_number=seat_number
                                                        registration.save()
                                                    tickets = mmodels.EventTicket.objects.filter(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)

                                    template_name = 'members/success.html'
                                    allObject['message'] = 'Welcome to ' + hostedevent.title +' day '+ eventday.day
                                    message = loader.render_to_string(template_name,allObject,request)
                                    template_name = 'members/attendee_event_manager.html'
                                    content = loader.render_to_string(template_name,allObject,request)
                                    output_data = {
                                            'header':hostedevent.title,
                                            'message':message,
                                            'attended':True,
                                            'content':content
                                                    }
                                    return JsonResponse(output_data)               
                                elif eventday.start_date_time.date > datetime.datetime.now().date:
                                    message = 'Sorry, this event is not available for registration today. Check again on ' + str(eventday.start_date_time.date)
                                    output_data = {
                                            'message':message,
                                                    }
                                    return JsonResponse(output_data) 
                                elif eventday.start_date_time.date < datetime.datetime.now().date:
                                    message = 'Sorry, this event is not available for registration today as it already ended on '+str(eventday.end_date_time)
                                    output_data = {
                                            'message':message,
                                                    }
                                    return JsonResponse(output_data)         
        message = 'No event available for registration'        
        output_data = {
                'modal_message':message,
                'verified':False,
                        }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        message = 'Event Not available'        
        output_data = {
                'modal_message':message,
                'verified':False,
                        }
        return JsonResponse(output_data)


@login_required
def hostqrcverification(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    qrcodeid = request.GET.get('registrationid')
    try:
        registration = mmodels.Registration.objects.get(registrationid=qrcodeid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
        registration.authorized=True
        registration.completed = True
        registration.save()
        allObject['registration'] = registration
        ticket =''
        tickets = mmodels.EventTicket.objects.filter(eventid=hostedevent.eventid)
        for eventticket in tickets:
            for eventregistration in eventticket.registrations.all():
                if registration == eventregistration:
                    ticket=eventticket
                    allObject['ticket']=ticket
        template_name = 'members/attendee_summary.html'
        message = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'message':message,
                'verified':True,
                        }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        allObject['registration'] = False
        template_name = 'members/attendee_summary.html'
        message = loader.render_to_string(template_name,allObject,request)        
        output_data = {
                'message':message,
                'verified':False,
                        }
        return JsonResponse(output_data)


@login_required
def viewevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/view_event.html'  
    member = allObject['member']            
    event = mmodels.Event.objects.get(eventid=eventid)
    # hostedevents = mmodels.HostedEvent.objects.filter(eventid=hostedevent.eventid)
    allObject['event'] = event
    # allObject['hostedevents'] = hostedevents

    allObject['attendeescount'] = mmodels.Registration.objects.filter(eventid=eventid,verified=True).count()
    return render(request,template_name,allObject)


@login_required
def manageevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/manage_event.html'        
    event = mmodels.Event.objects.get(eventid=eventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    if not hostedevent.one_day:
        if hostedevent.days.count() > 0:
            for eventday in hostedevent.days.all():
                updateeventday(eventday)
    updateeventstatus(hostedevent)
    hostedevent.refresh_from_db()
    daytickets = mmodels.EventTicket.objects.filter(eventid=eventid,hostedeventid=hostedeventid,day=True)
    allObject['daytickets'] = daytickets
    dayarrangements = mmodels.Arrangement.objects.filter(eventid=eventid,hostedeventid=hostedeventid,day=True)
    allObject['dayarrangements'] = dayarrangements
    allObject['event'] = event
    allObject['hostedevent'] = hostedevent
    allObject['attendeescount'] = mmodels.Registration.objects.filter(eventid=hostedevent.eventid,verified=True).count()
    return render(request,template_name,allObject)




@login_required
def deleteeventday(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    day = mmodels.EventDay.objects.get(eventid=eventid,hostedeventid=hostedeventid,dayid=dayid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    allObject['eventday'] = day
    if day.registrations.count() > 0:
        output_data = { 
                        'modal_message':'day cannot be deleted as it has one or more registrations',
                        'deleted':False
                    }
        return JsonResponse(output_data) 
    day.delete()
    hostedevent.save()
    updateeventstatus(hostedevent)
    message ='day deleted'
    return updatedeventdetails(request,hostedevent,allObject,message)                



@login_required
def eventdayregistration(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
   
    if member.profile_updated:
        eventday = mmodels.EventDay.objects.get(dayid=dayid, eventid=eventid,hostedeventid=hostedeventid) 
        allObject['eventday'] = eventday
        hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
        allObject['hostedevent'] = hostedevent
        try: 
            registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=dayid)
            message ='You are already registered to attend ' + eventday.title 
            output_data = {
            'heading':hostedevent.title,
            'modal_content':message,
            'registered':True,
                    }
            return JsonResponse(output_data)         
        except ObjectDoesNotExist:
            if hostedevent.one_time_ticketing:
                ticketrequired = True
                hostedeventtickets = mmodels.EventTicket.objects.filter(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
                ticketed = ''
                for ticket in hostedeventtickets:
                    for registration in ticket.registrations.all():
                        if member == registration.attendee:
                            ticketrequired =False
                            ticketed= ticket
                            break
                if ticketrequired:   
                    return buyticket(request,hostedevent,dayid=dayid)
                registered = registerattendee(allObject,hostedevent,ticket,dayid)
                if registered['registered']:
                    errors = updateeventstatus(hostedevent)
                    allObject['hostedevent']=hostedevent
                    template_name = 'members/success.html'
                    allObject['message'] = 'Congratulations! You have registered for ' + registered['eventtitle']
                    message = loader.render_to_string(template_name,allObject,request)
                    template_name = 'members/attendee_event_manager.html'
                    return attendeemanager(request,hostedevent,message)
            else:
                ticketrequired = True
                if eventday.ticket_required:
                    registration_full = True
                    if eventday.tickets.count() >0:
                        for ticket in eventday.tickets.all():
                            if ticket.full:
                                pass
                            else:
                                registration_full = False
                                break
                
                    else:
                        if eventday.full:
                            pass
                        else:
                            registration_full = False
                    if registration_full:
                        eventday.full = True
                        eventday.save()
                        output_data = { 
                                        'modal_message':'Registration for this event is currently full',
                                        
                                    }
                        return JsonResponse(output_data)
                    return buyticket(request,hostedevent,dayid=dayid)
                else:
                    registered = registerattendeedaywthoutticket(allObject,hostedevent,eventday)
                    if registered['registered']:
                        errors = updateeventstatus(hostedevent)
                        allObject['hostedevent']=hostedevent
                        template_name = 'members/success.html'
                        allObject['message'] = 'Congratulations! You have registered for ' + registered['eventtitle']
                        message = loader.render_to_string(template_name,allObject,request)
                        template_name = 'members/attendee_event_manager.html'
                        return attendeemanager(request,hostedevent,message)

                


@login_required
def eventdaydetails(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    eventday = mmodels.EventDay.objects.get(dayid=dayid, eventid=eventid,hostedeventid=hostedeventid) 
    allObject['eventday'] = eventday
    member = allObject['member']      
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    register = True
    current_event_registration = []
    for registration in eventday.registrations.all():
        if registration.attendee == member:
            allObject['registration'] = registration
            allObject['registered'] = True
            register = False
            current_event_registration = registration    
            if current_event_registration.authorized == True:
                allObject['attended'] =True
            break
    if hostedevent.verification_steps != '0':
        if hostedevent.start_date_time.date() == datetime.datetime.today().date():
            allObject['verify']=True

    allObject['register'] = register
    allObject['hostedevent'] = hostedevent
    allObject['registration'] = current_event_registration
    event_details_template = 'members/event_day_details.html'
    event_details = loader.render_to_string(event_details_template,allObject,request)
    output_data = { 
                    'modal_content':event_details,
                    'heading':eventday.title
                }
    return JsonResponse(output_data) 

    
@login_required
def eventdetails(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/event_details.html'  
    member = allObject['member']      
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    if hostedevent.published:
        buyticket = checkticket(allObject,hostedevent,)
        arrange = checkarrangement(allObject,hostedevent)
        register = checkregistration(allObject,hostedevent)
        allObject['buyticket'] = buyticket
        allObject['arrange'] = arrange
        allObject['registered'] = True
        allObject['register'] = register
        if hostedevent.one_time_ticketing:
            if buyticket:
                allObject['registered'] = False
                allObject['register'] = True
            else:
                registrations =mmodels.Registration.objects.filter(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedeventid)
                allObject['registrations'] = registrations
        if hostedevent.verification_steps != '0':
            if hostedevent.start_date_time.date() == datetime.datetime.today().date():
                allObject['verify']=True
    else:
        allObject['unavailable'] = True
    allObject['hostedevent'] = hostedevent
    return render(request,template_name,allObject)


def attendeemanager(request,hostedevent,message='Done',heading='Message', *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']      
    # try:
    registrations =mmodels.Registration.objects.filter(attendee=member,eventid=hostedevent.eventid)
    allObject['registrations'] = registrations
    allObject['registered'] = True
    if hostedevent.verification_steps != '0':
        if hostedevent.start_date_time.date() == datetime.datetime.today().date():
            allObject['verify']=True
    # except ObjectDoesNotExist:
    #     allObject['register'] = True
    # allObject['hostedevent'] = hostedevent
    buyticket = checkticket(allObject,hostedevent,)
    arrange = checkarrangement(allObject,hostedevent)
    register = checkregistration(allObject,hostedevent)
    allObject['buyticket'] = buyticket
    allObject['arrange'] = arrange
    allObject['registered'] = True
    allObject['register'] = register
    template_name = 'members/attendee_event_manager.html'
    content = loader.render_to_string(template_name,allObject,request)
    ticketbtn = 'members/ticket_btn.html'
    ticketbtncontent = loader.render_to_string(ticketbtn,allObject,request)
    output_data = {
            'modal_message':message,
            'content':content,
            'ticketbtn':ticketbtncontent,
            'buyticket':checkticket(allObject,hostedevent),
            'heading':heading,
                      }
    return JsonResponse(output_data)  



@login_required
def eventregistration(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):

    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    try:
        registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
        message ='You are already registered for this event'
        output_data = {
        'header':hostedevent.title,
        'modal_notification':message,
        'registered':True,
                }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        if hostedevent.days.count() > 0:
            return eventdays(request,hostedevent)
        allObject['hostedevent'] = hostedevent
        registration= registerattendee(allObject,hostedevent)

        if hostedevent.verification_steps == '0':
            registration.verified = True
            registration.completed = True
            registration.status = 'accredited'
            registration.accredited_by ='qrcode'
            registration.save()
        registration.refresh_from_db()
        upcomingevents =  list(mmodels.HostedEvent.objects.filter(
            end_date_time__gte = datetime.datetime.today().date(),open_to='adults'))
        upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
        parent = checkparent(member)
        if parent:
            childrenevents =  list(mmodels.HostedEvent.objects.filter(end_date_time__gte = datetime.datetime.now(),open_to='children'))
            upcomingevents.extend(childrenevents)
        allObject['upcomingevents'] =upcomingevents
        if registration.seat_number != '':
            seatnumber= registration.seat_number
            allObject['message'] = "Congratulations! You have registered for " + hostedevent.title +"<br> <span class='h2 text-darker uk-text-bold'> SEAT ID:</span> <span class='h2 uk-text-bold text-yellow'>"+seatnumber+'</span>'
        template_name = 'members/success.html'
        message = loader.render_to_string(template_name,allObject,request)
        updatecontenttemplate = 'members/upcoming_events.html'
        updatecontent = loader.render_to_string(updatecontenttemplate,allObject,request)
        output_data = {
                'modal_message':message,
                'updatecontent':updatecontent
                        }
        return JsonResponse(output_data)
    output_data = {
            'modal_message':'Registration failed',
                    }
    return JsonResponse(output_data)



@login_required
def eventdays(request,hostedevent, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    allObject['hostedevent'] = hostedevent
    registration_full = True
    
    template_name = 'members/event_days.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'heading':'<b>' +hostedevent.title + '</b> Days',
    'modal_content':content,
            }
    return JsonResponse(output_data)


@login_required
def buyticket(request,hostedevent=None,hostedeventid=None,eventid=None,  dayid=None,*args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    if hostedevent==None:
        hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)    
    allObject['hostedevent'] = hostedevent

    if hostedevent.one_time_ticketing:
        try:
            current_event_registration =mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,day=False)
            for ticket in hostedevent.tickets.all():
                if current_event_registration in ticket.registrations.all():
                    pass
                else:
                    allObject['buyhostedeventticket'] = True
        except ObjectDoesNotExist:
            allObject['register'] = True
            allObject['buyhostedeventticket'] = True
    else:
        if hostedevent.days.count() > 0:
            ticketabledays = []
            allObject['buydayticket'] = False
            for day in hostedevent.days.all():
                if day.ticket_required:
                    if day.tickets.count() >0:
                        try:
                            mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,dayid=day.dayid)
                        except ObjectDoesNotExist:
                            allObject['buydayticket'] = True
                            ticketabledays.append(day)
            allObject['ticketabledays']=ticketabledays
    template_name = 'members/buy_ticket.html'
    allObject['dayid']=dayid
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'heading':'<b>' +hostedevent.title + '</b> Ticket Purchase',
    'modal_content':content,
            }
    return JsonResponse(output_data) 





def checkarrangement(allObject,hostedevent):
    member = allObject['member']
    if hostedevent.one_time_arrangement:
        try:
            current_event_registration =mmodels.Registration.objects.filter(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
            return False
            allObject['registration'] = current_event_registration
            allObject['registered'] = True
            if hostedevent.verification_steps != '0':
                if hostedevent.start_date_time.date() == datetime.datetime.today().date():
                    allObject['verify']=True
            if current_event_registration.authorized == True:
                allObject['attended'] =True
        except ObjectDoesNotExist:
            return True
    else:
        allObject['arrange'] = False
        if hostedevent.days.count() > 0:
            for day in hostedevent.days.all():
                if day.arrange:
                        if day.arrangements.count() >0:
                            try:
                                mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,dayid=day.dayid)
                            except ObjectDoesNotExist:
                                return True
    return False




def checkregistration(allObject,hostedevent):
    member = allObject['member']
    if hostedevent.one_time_ticketing:
        if hostedevent.one_day:
            try:
                current_event_registration =mmodels.Registration.objects.get(attendee=member,hostedeventid=hostedevent.hostedeventid,eventid=hostedevent.eventid,day=False)
            except ObjectDoesNotExist:
                return True
    else:
        if hostedevent.days.count() > 0:
            for day in hostedevent.days.all():
                try:
                    registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=day.dayid)
                except ObjectDoesNotExist:
                    return True
    return False



def checkticket(allObject,hostedevent,):
    member = allObject['member']
    if hostedevent.one_time_ticketing:
        if hostedevent.one_day:
            try:
                current_event_registration =mmodels.Registration.objects.get(attendee=member,hostedeventid=hostedevent.hostedeventid,eventid=hostedevent.eventid,day=False)
            except ObjectDoesNotExist:
                return True
        else:
            if hostedevent.days.count() > 0:
                for day in hostedevent.days.all():
                    try:
                        registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=day.dayid)
                    except ObjectDoesNotExist:
                        return True
    else:
        if hostedevent.days.count() > 0:
            for day in hostedevent.days.all():
                try:
                    registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=day.dayid)
                except ObjectDoesNotExist:
                    return True
    return False

    # member = allObject['member']
    # if hostedevent.one_time_ticketing:
    #     try:
    #         current_event_registration =mmodels.Registration.objects.filter(attendee=member,hostedeventid=hostedevent.hostedeventid,eventid=hostedevent.eventid,)
    #         return False
    #     except ObjectDoesNotExist:
    #         return True

    # else:
    #     allObject['buyticket'] = False
    #     if hostedevent.days.count() > 0:
    #         for day in hostedevent.days.all():
    #             if day.ticket_required:
    #                     if day.tickets.count() >0:
    #                         try:
    #                             mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,dayid=day.dayid)
    #                         except ObjectDoesNotExist:
    #                             return True
    # return False


def updateeventday(eventday):
    eventday.full = False
    eventday.save()
    if eventday.tickets.count() >0:
        for ticket in eventday.tickets.all():
            if ticket.full:
                pass
            else:
                registration_full = False
                break
    else:
        if eventday.full:
            pass
        else:
            registration_full = False
    if registration_full:
        eventday.full = True
        eventday.save()
    
def updateeventstatus(event):
    event.editable = True
    event.publishable = True
    errors = []
    if event.days.count() >0:
        for eventday in event.days.all():
            eventday.error = False
            eventday.save()
    if event.registrations.count() >0:
        event.editable = False
        errors.append('Event has one or more registrations')

    if (not event.one_day and event.days.count() < 1) :
        event.publishable = False
        event.published = False
        errors.append('No day added to event')
    if (event.one_time_ticketing):
        if event.tickets.count() < 1:
            event.publishable = False
            event.published = False
            errors.append('No ticket added to event')
    if not event.one_time_ticketing:
        if event.days.count() >0:
            for day in event.days.all():
                if day.ticket_required:
                    if day.tickets.count() < 1:
                        day.error = True
                        day.save()
                        event.publishable = False
                        event.published = False
                        errors.append('Event day ' +day.title+' requires ticketing and none was added')
                    else:
                        day.error = False
                        day.save()
    if not event.one_time_arrangement:
        if event.days.count() >0:
            for day in event.days.all():
                if not day.ticket_required and day.arrange:
                    if day.arrangements.count() < 1:
                        day.error = True
                        day.save()
                        event.publishable = False
                        event.published = False
                        errors.append('Event day ' +day.title+' requires arrangement and none was added')
                    else:
                        day.error = False
                        day.save()

    if (event.one_time_arrangement and event.arrangements.count() < 1 and not event.one_time_ticketing):
            event.publishable = False
            event.published = False
            errors.append('No arrangement added to event')
    if (event.one_time_arrangement and event.arrangements.count() > 0 and not event.one_time_ticketing):
        for arrangement in event.arrangements.all():
            if arrangement.chairs_per_table == 0:
                event.publishable = False
                event.published = False
                errors.append('Arrangement with name ' +arrangement.name + ' needs to be updated')          
    if event.one_time_arrangement and event.one_time_ticketing:
        for ticket in event.tickets.all():
            if ticket.chairs_per_table == 0:
                event.publishable = False
                event.published = False
                errors.append('Ticket with name ' +ticket.name + ' needs to be updated')              
    event.save()
    return errors

def checkeventstatus(event):
    if event.published:     
        return True



@login_required
def unpublishevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    errors = updateeventstatus(hostedevent)
    
    hostedevent.published =False
    hostedevent.save()
    message='Event unpublished'
    return updatedeventdetails(request,hostedevent,allObject,message)


@login_required
def publishevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    errors = updateeventstatus(hostedevent)
    if hostedevent.publishable:
        hostedevent.published =True
        hostedevent.save()
        message='Event Published'
        return updatedeventdetails(request,hostedevent,allObject,message)
    else:
        erroroutput ="<ul class='text-danger p-0'>"
        errorlist = ''
        for error in errors:
            errorlist += '<li>' +error+'</li>'
        erroroutput += errorlist + '</ul>'
        output_data = { 
                        'done':False,
                        'modal_message':'<b>Event not published</b>' + erroroutput,
                        
                    }
        return JsonResponse(output_data)


def registerattendeedaywthticket(allObject,hostedevent,ticket,eventday):
    registration_id = hostedevent.initials+'00'+str(hostedevent.registrations.count()+1)+'-'+str(round(random()*1234567890))
    registration = mmodels.Registration.objects.create(registrationid=registration_id[0:8],attendee=allObject['member'],eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
    registration.refresh_from_db()
    hostedevent.registrations.add(registration)
    ticket.registrations.add(registration)
    ticket.save()
    registration.ticketid = ticket.ticketid
    registration.save()
    if hostedevent.verification_steps == '0':
        registration.verified = True
        registration.completed = True
        registration.save()
        if hostedevent.one_time_arrangement:
            for arrangement in hostedevent.arrangements.all():
                if arrangement.full:
                    pass
                else:
                    arrangement.registrations.add(registration)
                    registration.seat_number=arrangeattendee(arrangement,hostedevent,registration)
                    registration.day= True
                    registration.dayid= eventday.dayid
                    registration.save()
                    break
        else:
            if eventday.arrange:
                registration.seat_number=arrangeattendee(ticket,hostedevent,registration)
                registration.day= True
                registration.dayid= eventday.dayid
                registration.save()
        eventday.registrations.add(registration)
        eventday.save()
        eventtitle = eventday.title +' DAY ' + str(eventday.day)
        return {'eventtitle':eventtitle,'registered':True}
           




def registerattendeedaywthoutticket(allObject,hostedevent,eventday):
    registration_id = hostedevent.initials+'00'+str(hostedevent.registrations.count()+1)+'-'+str(round(random()*1234567890))
    registration = mmodels.Registration.objects.create(registrationid=registration_id[0:8],attendee=allObject['member'],eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
    registration.refresh_from_db()
    hostedevent.registrations.add(registration)
    registration.day= True
    registration.dayid= eventday.dayid
    registration.save()
    if hostedevent.verification_steps == '0':
        registration.verified = True
        registration.completed = True
        registration.save()
        if hostedevent.one_time_arrangement:
            for arrangement in hostedevent.arrangements.all():
                if arrangement.full:
                    pass
                else:
                    arrangement.registrations.add(registration)
                    registration.seat_number=arrangeattendee(arrangement,hostedevent,registration)
                    registration.arrangementid=arrangement.arrangementid
                    registration.save()
                    break
        else:
            if eventday.arrange:
                for arrangement in eventday.arrangements.all():
                    if arrangement.full:
                        pass
                    else:
                        arrangement.registrations.add(registration)
                        registration.seat_number=arrangeattendee(arrangement,hostedevent,registration)
                        registration.save()
                        break
        eventday.registrations.add(registration)
        eventday.save()
        eventtitle = eventday.title +' DAY ' + str(eventday.day)
        return {'eventtitle':eventtitle,'registered':True}
           


@login_required
def boughtticket(request,eventid=None,hostedeventid=None,ticketid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/event_details.html'  
    member = allObject['member']
    transaction_reference=request.POST.copy().get('reference')
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    ticket = mmodels.EventTicket.objects.get(ticketid=ticketid,eventid=eventid,hostedeventid=hostedeventid,)
    eventtitle=''
    if request.method == 'POST':
        try:
            registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,ticketid=ticket.ticketid)
            message ='You are already registered for this event'
            output_data = {
            'header':hostedevent.title,
            'message':message,
            'registered':True,
                    }
            return JsonResponse(output_data) 
        except ObjectDoesNotExist:
            if hostedevent.one_time_ticketing:
                if ticket.free:
                    registerattendee(allObject,hostedevent,ticket,dayid)

                else:
                    registration = mmodels.Registration.objects.create(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,payment_reference=transaction_reference or '')
                    hostedevent.registrations.add(registration)
                    ticket.registrations.add(registration)
                    ticket.save()
                    # hostedevent.attendees.add(member)
                    hostedevent.save()
                    hostedevent.refresh_from_db()
        errors = updateeventstatus(hostedevent)
        allObject['hostedevent']=hostedevent
        template_name = 'members/success.html'
        allObject['message'] = 'Congratulations! You have registered for ' + eventtitle
        message = loader.render_to_string(template_name,allObject,request)
        template_name = 'members/attendee_event_manager.html'
        return attendeemanager(request,hostedevent,message)




@login_required
def boughtdayticket(request,eventid=None,hostedeventid=None,ticketid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/event_details.html'  
    member = allObject['member']
    transaction_reference=request.POST.copy().get('reference')
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    ticket = mmodels.EventTicket.objects.get(ticketid=ticketid,eventid=eventid,hostedeventid=hostedeventid,)
    eventday = mmodels.EventDay.objects.get(dayid=dayid,eventid=eventid,hostedeventid=hostedeventid,)
    eventtitle=''
    if request.method == 'POST':
        try:
            registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,ticketid=ticket.ticketid)
            message ='You are already registered for this event'
            output_data = {
            'header':hostedevent.title,
            'message':message,
            'registered':True,
                    }
            return JsonResponse(output_data) 
        except ObjectDoesNotExist:
            # if hostedevent.one_time_ticketing:
            if ticket.free:
                registered = registerattendeedaywthticket(allObject,hostedevent,ticket,eventday)

            else:
                registration = mmodels.Registration.objects.create(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,payment_reference=transaction_reference or '')
                hostedevent.registrations.add(registration)
                ticket.registrations.add(registration)
                ticket.save()
                # hostedevent.attendees.add(member)
                hostedevent.save()
                hostedevent.refresh_from_db()
            registration_full = True
            if eventday.tickets.count() >0:
                for ticket in eventday.tickets.all():
                    if ticket.full:
                        pass
                    else:
                        registration_full = False
                        break
        
            else:
                if eventday.full:
                    pass
                else:
                    registration_full = False
            if registration_full:
                eventday.full = True
                eventday.save()
            errors = updateeventstatus(hostedevent)
            allObject['hostedevent']=hostedevent
            template_name = 'members/success.html'
            allObject['message'] = 'Congratulations! You have registered for ' + registered['eventtitle']
            message = loader.render_to_string(template_name,allObject,request)
            template_name = 'members/attendee_event_manager.html'
            return attendeemanager(request,hostedevent,message)

@login_required
def createeventarrangement(request,eventid=None,hostedeventid=None,action=None,dayid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    if request.method == 'POST':
        hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
        arrangement = uforms.createeventarrangement(request.POST)
        if arrangement.is_valid():
            arrangement.save()
            arrangement.instance.hostedeventid=hostedevent.hostedeventid
            arrangement.instance.eventid=hostedevent.eventid
            arrangement.instance.dayid=dayid
            arrangement.save()
            if dayid == 'None':
                hostedevent.arrangements.add(arrangement.instance)
                hostedevent.save()
                hostedevent.refresh_from_db()
                if hostedevent.one_time_arrangement:
                    for eventday in hostedevent.days.all():
                        eventday.arrangements.add(arrangement.instance)
                        eventday.save()           
            else:
                arrangement.instance.day=True
                eventday = mmodels.EventDay.objects.get(eventid=eventid,hostedeventid=hostedeventid,dayid=dayid)
                eventday.arrangements.add(arrangement.instance)
                arrangement.save()
            allObject['hostedevent'] = hostedevent
            updateeventstatus(hostedevent)

            if action == 'next':
                template_name = 'members/create_event_arrangement_modal.html'
                content = loader.render_to_string(template_name,allObject,request)
                event_details_template = 'members/hosted_event_manager.html'
                event_details = loader.render_to_string(event_details_template,allObject,request)
                output_data = { 
                                'done':True,
                                'message':'Arrangement added',
                                'modal_content':content,
                                'content':event_details,
                                'next':True
                                
                            }
                return JsonResponse(output_data)
                
            elif action =='exit':
                event_details_template = 'members/hosted_event_manager.html'
                event_details = loader.render_to_string(event_details_template,allObject,request)
                output_data = { 
                                'done':True,
                                'message':'Arrangement added',
                                'content':event_details,
                                'exit':True                              
                            }
                return JsonResponse(output_data)

    else:
        allObject['dayid']=dayid
        template_name = 'members/create_event_arrangement_modal.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = { 
                        'modal_content':content,    
                        'heading':'Add Arrangement'                    
                    }
        return JsonResponse(output_data)




@login_required
def createeventticket(request,eventid=None,hostedeventid=None,action=None,dayid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    event=mmodels.Event.objects.get(eventid=eventid)
    registrations = mmodels.Registration.objects.all()
    for registration in registrations:
        registration.delete()
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    if request.method == 'POST':
        ticket = uforms.createeventticket(request.POST)
        if ticket.is_valid():
            ticket.save()
            ticket.instance.hostedeventid=hostedevent.hostedeventid
            ticket.instance.eventid=hostedevent.eventid
            ticket.instance.dayid=dayid
            ticket.save()
            if dayid == 'None':
                hostedevent.tickets.add(ticket.instance)
                hostedevent.save()
                hostedevent.refresh_from_db()
                if hostedevent.one_time_ticketing:
                    for eventday in hostedevent.days.all():
                        eventday.tickets.add(ticket.instance)
                        eventday.save()           
            else:
                ticket.instance.day=True
                eventday = mmodels.EventDay.objects.get(eventid=eventid,hostedeventid=hostedeventid,dayid=dayid)
                eventday.tickets.add(ticket.instance)
                ticket.save()
            errors= updateeventstatus(hostedevent)
            allObject['hostedevent'] = hostedevent

            if action == 'next':
                template_name = 'members/create_event_ticket_modal.html'
                content = loader.render_to_string(template_name,allObject,request)
                event_details_template = 'members/hosted_event_manager.html'
                event_details = loader.render_to_string(event_details_template,allObject,request)
                output_data = { 
                                'done':True,
                                'message':'Ticket added',
                                'modal_content':content,
                                'content':event_details,
                                'next':True
                                
                            }
                return JsonResponse(output_data)
            elif action =='exit':
                event_details_template = 'members/hosted_event_manager.html'
                event_details = loader.render_to_string(event_details_template,allObject,request)
                output_data = { 
                                'done':True,
                                'message':'Ticket added',
                                'content':event_details,
                                'exit':True,
                                # 'url':redirectaction
                            }
                return JsonResponse(output_data)
        else:

            output_data = {
                'eventimageadded':False,
                'message':'image not added because form is invalid',
                            }
            return JsonResponse(output_data)
    else:
        allObject['dayid']=dayid
        template_name = 'members/create_event_ticket_modal.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = { 
                'heading':'Add Ticket',
                        'eventcreated':True,
                        'modal_content':content,
                        
                        
                    }
        return JsonResponse(output_data)


@login_required
def createeventday(request,eventid=None,hostedeventid=None,action=None,scope=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    event=mmodels.Event.objects.get(eventid=eventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    if request.method == 'POST':
        parent_thumbnail = str(request.POST.copy().get('parent_thumbnail'))
        day = uforms.addeventday(request.POST,request.FILES)
        specialoffer = str(request.POST.copy().get('offer'))
        arrange = str(request.POST.copy().get('arrange'))
        end_date_time_str = str(request.POST.copy().get('end_date_time'))
        end_date_time_obj = datetime.datetime.strptime(end_date_time_str, '%m/%d/%Y %I:%M %p')
        start_date_time_str = str(request.POST.copy().get('start_date_time'))
        start_date_time_obj = datetime.datetime.strptime(start_date_time_str, '%m/%d/%Y %I:%M %p')
        ticketing = str(request.POST.copy().get('ticketing'))
        if ticketing == 'yes':
            ticketing = True
        elif ticketing == 'no':
            ticketing = False
        if specialoffer == 'yes':
            specialoffer = True
        elif specialoffer == 'no':
            specialoffer = False
        if arrange == 'yes':
            arrange = True
        elif arrange == 'no':
            arrange = False
        end_date_time_str = str(request.POST.copy().get('end_date_time'))
        end_date_time_obj = datetime.datetime.strptime(end_date_time_str, '%m/%d/%Y %I:%M %p')
        start_date_time_str = str(request.POST.copy().get('start_date_time'))
        start_date_time_obj = datetime.datetime.strptime(start_date_time_str, '%m/%d/%Y %I:%M %p')
        eventday = mmodels.EventDay.objects.create(arrange=arrange,special_offer=specialoffer, ticket_required=ticketing,
        eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,
        end_date_time=end_date_time_obj, start_date_time=start_date_time_obj, title=str(request.POST.copy().get('title')), 
        day=int(request.POST.copy().get('day_number')), full_description=str(request.POST.copy().get('full_description')),
        short_description=str(request.POST.copy().get('short_description')))
        eventday.refresh_from_db()
        hostedevent.days.add(eventday)
        eventday.full_description=str(request.POST.copy().get('full_description'))
        eventday.save()
        updateeventstatus(hostedevent)
        if day.is_valid():
            eventdayinstance = uforms.addeventday(request.POST,request.FILES,instance=eventday)
            eventdayinstance.save()
            eventday.refresh_from_db()        
        elif parent_thumbnail == 'yes':         
            eventday.thumbnail = hostedevent.thumbnail
            eventday.save()
        else:
            eventday.thumbnail = hostedevent.thumbnail
            eventday.save()


        if action == 'next':
            if scope =='modal':
                template_name = 'members/create_event_day.html'
                content = loader.render_to_string(template_name,allObject,request)
                event_details_template = 'members/hosted_event_manager.html'
                event_details = loader.render_to_string(event_details_template,allObject,request)
                output_data = { 
                                'eventdaycreated':True,
                                'message':'day added',
                                'full_modal_content':content,
                                'content':event_details,
                                'next':True
                                
                            }
                return JsonResponse(output_data)
        elif action =='exit':
                if scope == 'modal':
                    event_details_template = 'members/hosted_event_manager.html'
                    event_details = loader.render_to_string(event_details_template,allObject,request)
                    output_data = { 
                                    'eventdaycreated':True,
                                    'message':'day added',
                                    'content':event_details,
                                    'exit':True
                                    
                                }
                    return JsonResponse(output_data)
    else:
           
        template_name = 'members/create_event_day.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = { 
                        'heading':'Add Event Day',
                        'full_modal_content':content,
                        
                    }
        return JsonResponse(output_data)


@login_required
def editeventday(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    event=mmodels.Event.objects.get(eventid=eventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    eventday = mmodels.EventDay.objects.get(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=dayid)
    allObject['hostedevent'] = hostedevent
    allObject['eventday'] = eventday
    if request.method == 'POST':
        if eventday.registrations.count() > 0:
            output_data = { 
                        'modal_message':'Day cannot be edited as it has one or more registrations',
                        'deleted':False
                    }
        return JsonResponse(output_data)
        day = uforms.addeventday(request.POST,request.FILES)
        # if day.is_valid():
        parent_thumbnail = str(request.POST.copy().get('parent_thumbnail'))
        day = uforms.addeventday(request.POST,request.FILES)
        specialoffer = str(request.POST.copy().get('offer'))
        arrange = str(request.POST.copy().get('arrange'))
        end_date_time_str = str(request.POST.copy().get('end_date_time'))
        end_date_time_obj = datetime.datetime.strptime(end_date_time_str, '%m/%d/%Y %I:%M %p')
        start_date_time_str = str(request.POST.copy().get('start_date_time'))
        start_date_time_obj = datetime.datetime.strptime(start_date_time_str, '%m/%d/%Y %I:%M %p')
        ticketing = str(request.POST.copy().get('ticketing'))
        if ticketing == 'yes':
            ticketing = True
        elif ticketing == 'no':
            ticketing = False
        if specialoffer == 'yes':
            specialoffer = True
        elif specialoffer == 'no':
            specialoffer = False
        if arrange == 'yes':
            arrange = True
        elif arrange == 'no':
            arrange = False
        eventday = mmodels.EventDay.objects.filter(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=dayid).update(
        end_date_time=end_date_time_obj, start_date_time=start_date_time_obj, title= str(request.POST.copy().get('title')),arrange=arrange,special_offer=specialoffer, ticket_required=ticketing,)
        eventday = mmodels.EventDay.objects.get(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=dayid)
        eventdayinstance = uforms.addeventday(request.POST,request.FILES,instance=eventday)
        hostedevent.days.add(eventday)
        eventdayinstance.save()
        if day.is_valid():
            eventdayinstance = uforms.addeventday(request.POST,request.FILES,instance=eventday)
            eventdayinstance.save()
            eventday.refresh_from_db()        
        elif parent_thumbnail == 'yes':         
            eventday.thumbnail = hostedevent.thumbnail
            eventday.save()
        else:
            eventday.thumbnail = hostedevent.thumbnail
            eventday.save()
        eventday.refresh_from_db()
        message = 'day edited'
        return updatedeventdetails(request,hostedevent,allObject,message)
        # event_details_template = 'members/hosted_event_manager.html'
        # event_details = loader.render_to_string(event_details_template,allObject,request)
        # output_data = { 
        #                 'done':True,
        #                 'message':'day edited',
        #                 'content':event_details,                            
        #             }
        # return JsonResponse(output_data)
    else:
           
        template_name = 'members/edit_event_day.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = { 
                        'full_modal_content':content,                        
                    }
        return JsonResponse(output_data)          




@login_required
def verifyevent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    if member.profile_updated:
        try:
            hostedevent = mmodels.HostedEvent.objects.get(eventid=request.GET.get('eventid'))
            ongoingevents = list(mmodels.HostedEvent.objects.filter(end_date_time__gt = datetime.datetime.now(),start_date_time__lt=datetime.datetime.now()))
            upcomingevents =  list(mmodels.HostedEvent.objects.filter(start_date_time__gt = datetime.datetime.now()))
            pastevents =  list(mmodels.HostedEvent.objects.filter(end_date_time__lt = datetime.datetime.now(),start_date_time__lt=datetime.datetime.now()))
            if event in ongoingevents:
                if member in hostedevent.attendees.all():
                    message ='Your attendance has previously been recorded'
                    output_data = {
                        'message':message,
                        'attended':True
                                }
                    return JsonResponse(output_data)
                else:            
                    hostedevent.attendees.add(member)
                    hostedevent.save()
                    template_name = 'members/success.html'
                    allObject['message'] = 'Congratulations, your attendance has been recorded'
                    successcontent = loader.render_to_string(template_name,allObject,request)
                    output_data = {
                        'message':successcontent,
                        'attended':True
                                }
                    return JsonResponse(output_data)
            else:
                output_data = {
                    'message':'is not available for attendance',
                    'past':True
                            }
                return JsonResponse(output_data)
  
        except ObjectDoesNotExist:
                output_data = {
                    'message':'not found',
                            }
                return JsonResponse(output_data)
    else:
        return updateprofileform(request, *args, **kwargs)


@login_required
def hostevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    event=mmodels.Event.objects.get(eventid=eventid)
    allObject['event']=event
    if request.method == 'POST':
        form = uforms.hostevent(request.POST,request.FILES)
        if form.is_valid():

            one_day = str(request.POST.copy().get('one_time_arrangement'))

            arrange = str(request.POST.copy().get('one_time_arrangement'))
            verification_steps = str(request.POST.copy().get('verification'))
            end_date_time_str = str(request.POST.copy().get('end_date_time'))
            end_date_time_obj = datetime.datetime.strptime(end_date_time_str, '%m/%d/%Y %I:%M %p')
            start_date_time_str = str(request.POST.copy().get('start_date_time'))
            start_date_time_obj = datetime.datetime.strptime(start_date_time_str, '%m/%d/%Y %I:%M %p')
            ticketing = str(request.POST.copy().get('one_time_ticketing'))
            if ticketing == 'yes':
                ticketing = True
            elif ticketing == 'no':
                ticketing = False
            # if specialoffer == 'yes':
            #     specialoffer = True
            # elif specialoffer == 'no':
            #     specialoffer = False
            if one_day == 'yes':
                one_day = True
            elif one_day == 'no':
                one_day = False
            if arrange == 'yes':
                arrange = True
            elif arrange == 'no':
                arrange = False
            open_to = request.POST.copy().get('open_to')
            hostedevent = mmodels.HostedEvent.objects.create(open_to=open_to, one_day=one_day, one_time_arrangement=arrange, eventid=eventid, verification_steps=verification_steps, end_date_time=end_date_time_obj, start_date_time=start_date_time_obj, title=form.cleaned_data['title'],)
            hostedevent.refresh_from_db()
            hostedeventinstance = uforms.hostevent(request.POST,request.FILES,instance=hostedevent)
            hostedeventinstance.save()
            hostedevent.save()
            hostedevent.refresh_from_db()
            if hostedevent.thumbnail:
                pass
            else:
                hostedevent.thumbnail = event.thumbnail
                hostedevent.save()
            if arrange:
                for eventday in hostedevent.days.all():
                    eventday.arrange = True
                    eventday.save() 
            allObject['hostedevent'] = hostedevent
            event.hosted_events.add(hostedevent)
            template_name = 'members/success.html'
            allObject['message'] = hostedevent.title + ' hosted successfully'
            successcontent = loader.render_to_string(template_name,allObject,request)
            template_name = 'members/hosted_events.html'
            content = loader.render_to_string(template_name,allObject,request)
            output_data = { 
                            'done':True,
                            'modal_message':successcontent,
                            'content':content,
                            
                        }
            return JsonResponse(output_data) 
        else:
            allObject['url'] = request.get_full_path()
            template_name ='members/host_event.html'
            allObject['form'] = form
            content = loader.render_to_string(template_name,allObject,request)
            output_data = {
                'done':False,
                'message':'not hosted',
                                'modal_content':content,
                            }
            return JsonResponse(output_data)  

    else:
        allObject = inherit(request, *args, **kwargs)
        template_name = 'members/host_event.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'heading':'Host Event',
                        }
        return JsonResponse(output_data)  
        return render(request,template_name,allObject)



@login_required
def createevent(request, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    if request.method == 'POST':
        form = uforms.addevent(request.POST,request.FILES)
        if form.is_valid():
            reoccur = str(request.POST.copy().get('reoccur'))
            frequency = str(request.POST.copy().get('frequency'))
            if reoccur == 'yes':
                reoccur = True
            elif reoccur == 'no':
                reoccur = False
            event = mmodels.Event.objects.create(reoccur=reoccur,reoccurance_frequency=frequency, title=form.cleaned_data['title'], )
            event.refresh_from_db()
            eventinstance = uforms.addevent(request.POST,request.FILES,instance=event)
            eventinstance.save()
            event.save()
            redirectaction = redirect('member_view_event',eventid=event.eventid)
            event.refresh_from_db()
            allObject['event'] = event
            output_data = { 
                            'eventcreated':True,
                            'message':'created',
                            'url': redirectaction.url,
                            
                        }
            return JsonResponse(output_data) 
        else:
            allObject['url'] = request.get_full_path()
            template_name ='members/create_event.html'
            allObject['form'] = form
            content = loader.render_to_string(template_name,allObject,request)
            output_data = {
                'eventadded':False,
                'message':'not added',
                                'modal_content':content,
                            }
            return JsonResponse(output_data)  

    else:
        allObject = inherit(request, *args, **kwargs)
        template_name = 'members/create_event.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'heading':'Create Event',
                        }
        return JsonResponse(output_data)  
        return render(request,template_name,allObject)



@login_required
def editevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent

    if request.method == 'POST':
        # form = uforms.editevent(request.POST,request.FILES)
        # if form.is_valid():
        attendance_limit = str(request.POST.copy().get('attendance_limit'))
        title = str(request.POST.copy().get('title'))
        specialoffer = str(request.POST.copy().get('offer'))
        arrange = str(request.POST.copy().get('arrange'))
        verification_steps = str(request.POST.copy().get('verification'))
        end_date_time_str = str(request.POST.copy().get('end_date_time'))
        end_date_time_obj = datetime.datetime.strptime(end_date_time_str, '%m/%d/%Y %I:%M %p')
        start_date_time_str = str(request.POST.copy().get('start_date_time'))
        start_date_time_obj = datetime.datetime.strptime(start_date_time_str, '%m/%d/%Y %I:%M %p')
        ticketing = str(request.POST.copy().get('ticketing'))
        if ticketing == 'yes':
            ticketing = True
        elif ticketing == 'no':
            ticketing = False
        if specialoffer == 'yes':
            specialoffer = True
        elif specialoffer == 'no':
            specialoffer = False
        if arrange == 'yes':
            arrange = True
        elif arrange == 'no':
            arrange = False
        hostedevent = mmodels.HostedEvent.objects.filter(eventid=eventid).update(arrange=arrange,special_offer=specialoffer, verification_steps=verification_steps, end_date_time=end_date_time_obj, start_date_time=start_date_time_obj, title=title,
        ticket_required=ticketing, attendance_limit=attendance_limit)
        event=mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedevent.hostedeventid)
        hostedevent.refresh_from_db()
        eventinstance = uforms.addevent(request.POST,request.FILES,instance=event)
        eventinstance.save()
        hostedevent.save()
        hostedevent.refresh_from_db()
        output_data = { 
                        'eventedited':True,
                        'message':'edited',
                        'exit':True,
                        
                    }
        return JsonResponse(output_data)                
        # else:
        #     allObject['url'] = request.get_full_path()
        #     template_name ='members/create_event.html'
        #     allObject['form'] = form
        #     content = loader.render_to_string(template_name,allObject,request)
        #     output_data = {
        #         'eventadded':False,
        #         'message':'not added',
        #                         'modal_content':content,
        #                     }
        #     return JsonResponse(output_data)  

    else:
        template_name = 'members/edit_event.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'header':'Edit '+ hostedevent.title,
                        }
        # return JsonResponse(output_data)  
        return render(request,template_name,allObject)

@login_required
def edithostedevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    event = mmodels.Event.objects.get(eventid=eventid,)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)

    allObject['hostedevent'] = hostedevent
    errors= updateeventstatus(hostedevent)
    if not hostedevent.editable:
        erroroutput ="<ul class='text-danger p-0'>"
        errorlist = ''
        for error in errors:
            errorlist += '<li>' +error+'</li>'
        erroroutput += errorlist + '</ul>'
        output_data = { 
                        'done':False,
                        'modal_message':'<b>Event cannot be edited</b>' + erroroutput,
                        
                    }
        return JsonResponse(output_data)
    if request.method == 'POST':
        # form = uforms.edithostedevent(request.POST,request.FILES)
        # if form.is_valid():
        one_day = str(request.POST.copy().get('one_day'))

        attendance_limit = str(request.POST.copy().get('attendance_limit'))
        title = str(request.POST.copy().get('title'))
        specialoffer = str(request.POST.copy().get('offer'))
        arrange = str(request.POST.copy().get('one_time_arrangement'))
        verification_steps = str(request.POST.copy().get('verification'))
        end_date_time_str = str(request.POST.copy().get('end_date_time'))
        end_date_time_obj = datetime.datetime.strptime(end_date_time_str, '%m/%d/%Y %I:%M %p')
        start_date_time_str = str(request.POST.copy().get('start_date_time'))
        start_date_time_obj = datetime.datetime.strptime(start_date_time_str, '%m/%d/%Y %I:%M %p')
        ticketing = str(request.POST.copy().get('one_time_ticketing'))
        if ticketing == 'yes':
            ticketing = True
        elif ticketing == 'no':
            ticketing = False
        # if specialoffer == 'yes':
        #     specialoffer = True
        # elif specialoffer == 'no':
        #     specialoffer = False
        if one_day == 'yes':
            one_day = True
        elif one_day == 'no':
            one_day = False
        if arrange == 'yes':
            arrange = True
        elif arrange == 'no':
            arrange = False
        # if hostedevent.ticket_required and ticketing == False:
        #         if hostedevent.tickets.count() > 0:
        #             for ticket in hostedevent.tickets.all():
        #                 if ticket.registrations.count() > 0:
        #                     output_data = { 
        #                                     'eventedited':False,
        #                                     'message':"This event couldn't be edited as already existing tickets have some subscribers",
                                            
        #                                 }
        #                     return JsonResponse(output_data)
        hostedevent=mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
        if hostedevent.one_time_ticketing:
            if not ticketing:
                for ticket in hostedevent.tickets.all():
                    ticket.delete()
            for arrangement in hostedevent.arrangements.all():
                arrangement.delete()
        if hostedevent.one_time_arrangement and not arrange:
            for arrangement in hostedevent.arrangements.all():
                arrangement.delete()
        if not hostedevent.one_day and one_day:
            for day in hostedevent.days.all():
                day.delete()       
        editedhostedevent = mmodels.HostedEvent.objects.filter(eventid=eventid,hostedeventid=hostedevent.hostedeventid).update(one_day=one_day, one_time_arrangement=arrange, verification_steps=verification_steps, end_date_time=end_date_time_obj, start_date_time=start_date_time_obj, title=title,
        one_time_ticketing=ticketing)
        hostedevent.refresh_from_db()
        eventinstance = uforms.hostevent(request.POST,request.FILES,instance=hostedevent)
        eventinstance.save()
        errors= updateeventstatus(hostedevent)
        # redirectionaction = redirect('manage_event',eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid).url
        allObject['hostedevent'] = hostedevent

        template_name = 'members/hosted_event_manager.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = { 
                        'done':True,
                        'message':'edited',
                        'content':content,
                        
                    }
        return JsonResponse(output_data)

    else:
        template_name = 'members/edit_hosted_event.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'heading':'Edit '+ hostedevent.title,
                        }
        return JsonResponse(output_data)  
        # return render(request,template_name,allObject)

@login_required
def updatedeventdetails(request,hostedevent,allObject,message):
    errors= updateeventstatus(hostedevent)
    allObject['hostedevent'] = hostedevent
    # template_name = 'members/create_event_ticket_modal.html'
    # content = loader.render_to_string(template_name,allObject,request)
    event_details_template = 'members/hosted_event_manager.html'
    event_details = loader.render_to_string(event_details_template,allObject,request)
    output_data = { 
                    'done':True,
                    'message':message,
                    # 'modal_content':content,
                    'content':event_details,
                    
                }
    return JsonResponse(output_data)

@login_required
def editticket(request,eventid=None,hostedeventid=None,ticketid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    # for ticket in hostedevent.tickets.all():
    #     ticket.eventid=hostedevent.eventid
    #     ticket.save() 
    ticket = mmodels.EventTicket.objects.get(eventid=eventid,ticketid=ticketid,hostedeventid=hostedevent.hostedeventid)
    allObject['hostedevent'] = hostedevent
    allObject['ticket'] = ticket
    if ticket.registrations.count() > 0:
        output_data = { 
                        'modal_message':'Ticket cannot be edited',
                        'deleted':False
                    }
        return JsonResponse(output_data) 
    if request.method == 'POST':
        form = uforms.createeventticket(request.POST,instance=ticket)
        if form.is_valid():
            form.save()
            # if hostedevent.arrange:
            #     hostedevent.arrangement_update_needed = True
            hostedevent.save()
            message = 'ticket edited'
            return updatedeventdetails(request,hostedevent, allObject,message)
                           

    else:
        template_name = 'members/edit_event_ticket.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'heading':'Edit '+ ticket.name,
                        }
        return JsonResponse(output_data)

@login_required
def editarrangement(request,eventid=None,hostedeventid=None,arrangementid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    arrangement = mmodels.Arrangement.objects.get(eventid=eventid,arrangementid=arrangementid,hostedeventid=hostedeventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    errors = updateeventstatus(hostedevent)
    allObject['hostedevent'] = hostedevent
    allObject['arrangement'] = arrangement
    if arrangement.registrations.count() > 0:
        output_data = { 
                        'modal_message':'Arrangement cannot be edited as it has one or more registrations',
                        'deleted':False
                    }
        return JsonResponse(output_data) 

    if request.method == 'POST':
        form = uforms.createeventarrangement(request.POST,instance=arrangement)
        if form.is_valid():
            form.save()
            hostedevent.arrangement_update_needed = True
            hostedevent.save()
            arrangement.save()
            message = 'arrangement edited'
            return updatedeventdetails(request,hostedevent,allObject,message)
    else:
        template_name = 'members/edit_event_arrangement.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'heading':'Edit '+ arrangement.name,
                        }
        return JsonResponse(output_data)  



@login_required
def deleteticket(request,eventid=None,hostedeventid=None,ticketid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    ticket = mmodels.EventTicket.objects.get(eventid=eventid,ticketid=ticketid,hostedeventid=hostedeventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    # event = mmodels.HostedEvent.objects.get(eventid=eventid,)
    allObject['hostedevent'] = hostedevent
    allObject['ticket'] = ticket
    if ticket.registrations.count() > 0:
        erroroutput ="<ul class='text-danger p-0'>"
        errors = ['Ticket has one or more registrations']
        errorlist = ''
        for error in errors:
            errorlist += '<li>' +error+'</li>'
        erroroutput += errorlist + '</ul>'
        output_data = { 
                        'done':False,
                        'modal_message':'<b>Ticket cannot be deleted</b>' + erroroutput,
                        
                    }
        return JsonResponse(output_data)        
    ticket.delete()
    hostedevent.save()
    updateeventstatus(hostedevent)
    message ='Ticket deleted'
    return updatedeventdetails(request,hostedevent,allObject,message)
 


@login_required
def deletearrangement(request,eventid=None,hostedeventid=None,arrangementid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    arrangement = mmodels.Arrangement.objects.get(eventid=eventid,arrangementid=arrangementid,hostedeventid=hostedeventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    allObject['arrangement'] = arrangement
    if arrangement.registrations.count() > 0:
        output_data = { 
                        'modal_message':'Arrangement cannot be deleted as it has one or more registrations',
                        'deleted':False
                    }
        return JsonResponse(output_data) 
    arrangement.delete()
    hostedevent.save()
    updateeventstatus(hostedevent)
    message ='Arrangement deleted'
    return updatedeventdetails(request,hostedevent,allObject,message)                


@login_required
def myprofile(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'members/profile.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'modal_content':content,
            'header':'My Profile',
                    }
    return JsonResponse(output_data)  


@login_required
def dashboardcontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    if member.profile_updated:
        template_name = 'members/dashboard_content.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'header':'Due balance: ' + 'N2000',
                        }
        return JsonResponse(output_data)  
    else:
        return updateprofileform(request, *args, **kwargs)


@login_required
def informationdeskcontent(request,content=None,cid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    if member.profile_updated:
        try:
            if str(content).lower() == 'article':
                reqcontent = mmodels.Article.objects.get(contentid=cid)
            elif str(content).lower() == 'announcement':
                reqcontent = mmodels.Announcement.objects.get(contentid=cid)
            template_name = 'members/information_desk_content.html'
            allObject['content']=reqcontent
            content = loader.render_to_string(template_name,allObject,request)
            output_data = {
                    'modal_content':content,
                    'header':reqcontent.title,
                            }
            return JsonResponse(output_data) 
        except ObjectDoesNotExist:
            output_data = {
            'content':'Content not found',
                    }
            return JsonResponse(output_data)   
         
    else:
        return updateprofileform(request, *args, **kwargs)


@login_required
def events(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    if member.profile_updated:
        upcomingevents =  list(mmodels.HostedEvent.objects.filter(start_date_time__gt = datetime.datetime.now()))
        try:
            todayshostedevent = mmodels.HostedEvent.objects.get(end_date_time__gt=datetime.datetime.now(),start_date_time__date=datetime.datetime.today().date())
            if todayshostedevent.start_date_time < datetime.datetime.now() and todayshostedevent.end_date_time > datetime.datetime.now():
                allObject['eventongoing'] =True         
        except ObjectDoesNotExist:
            todaysevent=''
            allObject['eventongoing'] =False
        upcomingevents.sort(key=lambda x: x.date_time_added,reverse=True)

        allObject['upcomingevents'] =upcomingevents
        pastevents =  list(mmodels.HostedEvent.objects.filter(end_date_time__gt = datetime.datetime.now(),start_date_time__lt=datetime.datetime.now()))
        pastevents.sort(key=lambda x: x.date_time_added,reverse=True)
        allObject['pastevents'] =pastevents
        allObject['todaysevent'] =todaysevent
        template_name = 'members/events.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                        }
        return JsonResponse(output_data)  
    else:
        return updateprofileform(request, *args, **kwargs)




@login_required
def announcements(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    if member.profile_updated:
        announcements =  list(mmodels.Announcement.objects.all())
        announcements.sort(key=lambda x: x.date_time_added,reverse=True)
        allObject['announcements'] =announcements
        template_name = 'members/announcements.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'header':'Announcements',
                        }
        return JsonResponse(output_data)  
    else:
        return updateprofileform(request, *args, **kwargs)




@login_required
def announcementdetails(request,announcementid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    if member.profile_updated:
        announcement = mmodels.Announcement.objects.get(contentid=announcementid)
        allObject['announcement'] = announcement
        template_name = 'members/announcement_details.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'message':content,
                        }
        return JsonResponse(output_data)  
    else:
        return updateprofileform(request, *args, **kwargs)






@login_required
def updateprofile(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    if request.method == 'POST':
        user = request.user
        member =allObject['member']
        # secretanswer = str(request.POST.copy().get('sqa'))
        # secretquestion =str(request.POST.copy().get('sq'))
        phone = str(request.POST.copy().get('phone'))
        number = str(request.POST.copy().get('street_number'))
        street = str(request.POST.copy().get('street'))
        city = str(request.POST.copy().get('city'))
        lga = str(request.POST.copy().get('lga'))
        state= str(request.POST.copy().get('state'))
        nearest_bus_stop= str(request.POST.copy().get('busstop'))
        landmark= str(request.POST.copy().get('landmark'))
        dob = request.POST.copy().get('dob')
        gender= str(request.POST.copy().get('gender'))
        marriage= str(request.POST.copy().get('marriage'))
        # member.secret_question = secretquestion
        # member.secret_answer = secretanswer
        member.phone_number = phone
        member.lga = lga
        member.state = state
        member.street_number = number
        member.city = city
        member.street = street
        member.nearest_bus_stop = nearest_bus_stop
        member.landmark = landmark
        member.date_of_birth = dob

        member.gender = gender
        member.marital_status = marriage

        member.save()
        message = "Your profile has been updated"
        member.profile_updated = True
        member.save()
        profile_updated = True
        subject = 'Profile Updated'
        mail_body = 'Your profile has been updated'
        template_name = 'members/success.html'
        allObject['message'] = 'Your profile updated'
        successcontent = loader.render_to_string(template_name,allObject,request)
        template_name = 'members/dashboard_content.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'profile_updated':profile_updated,
             'modal_content':content,
             'successcontent':successcontent,
             'header':'Due balance: ' + 'N2000'
                        }
        message = render_to_string('members/update_profile_email.html', {
               'message':mail_body,
               'user':user
            })
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ] 
        # send_mail( subject, message, email_from, recipient_list ) 
        return JsonResponse(output_data)    

    else:
        member =allObject['member']   
        template_name = 'members/update_profile.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'modal_content':content,
                            'header':'Update Profile'
                        }
        return JsonResponse(output_data)    


def videos(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    videos = list(mmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    allObject['videos'] =videos
    template_name = 'members/videos.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'modal_content':content,
                        }
    return JsonResponse(output_data)

