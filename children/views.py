from excel_response import ExcelResponse
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.db.models.lookups import Regex
from django.http.response import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
import children
from general import forms as gforms
from django.core.exceptions import ObjectDoesNotExist
from general import models as gmodels
from random import random
from django.db import utils
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
from children import models as chmodels
from children import forms as chforms
from members import forms as uforms
from members.views import checkmemberstatus,confirmemailpage,arrangeattendee
from general.views import logrequest
allObject = {}


def inherit(request, *args, **kwargs):
    allObject={}
    # current_user = mmodels.Member.objects.get(user=User.objects.get(email=request.user.email),dependant=False)
    # allObject['member'] = current_user
    # logrequest(request,allObject['member'].memberid)
    # if current_user.briefly_suspended:
    #     allObject['suspended'] = True
    try:
        settings = list(gmodels.General.objects.all())[0]
    except IndexError:
        settings = []
    # try:
    #     teacher = chmodels.Teacher.objects.get(member = allObject['member'])
    # except ObjectDoesNotExist:
    #     teacher = False
    allObject['settings'] = settings
    allObject['server_timestamp'] = math.floor(datetime.datetime.now().timestamp())
    # try:
    #     parent = chmodels.Parent.objects.get(member = allObject['member'])
    # except ObjectDoesNotExist:
    #     parent =[]
    # allObject['parent'] = parent    
    # allObject['teacher'] = teacher    

    return allObject

@login_required
def checkparent(member):
    if member.has_dependants:
        return True
    
    return False

@login_required
def unsuspend(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    member.suspension_count=0
    member.briefly_suspended= False
    member.save()
    output_data = {
            'unsuspended':True
                    }
    return JsonResponse(output_data)  








def pupilsperclass(request,childage,*args,**kwargs):
    existingdependants = chmodels.LraMembersChildren.objects.all().exclude(del_flg='Y')
    classpupils = []
    if childage == 'all':
        for existingdependant in existingdependants:
            try:
                dateofbirth = datetime.datetime(existingdependant.c_date_of_birth.year,existingdependant.c_date_of_birth.month,existingdependant.c_date_of_birth.day)
                agef = ((datetime.datetime.timestamp(datetime.datetime.now()) - datetime.datetime.timestamp(dateofbirth))/31556952)
                age = datetime.datetime.now().year - dateofbirth.year
                
                if age >13 or age <4:
                    
                    continue
                else:
                    classpupils.append(existingdependant)

            except Exception:
                pass
    else:
        for existingdependant in existingdependants:
            try:
                dateofbirth = datetime.datetime(existingdependant.c_date_of_birth.year,existingdependant.c_date_of_birth.month,existingdependant.c_date_of_birth.day)
                agef = ((datetime.datetime.timestamp(datetime.datetime.now()) - datetime.datetime.timestamp(dateofbirth))/31556952)
                age = datetime.datetime.now().year - dateofbirth.year
                
                if age >13:
                    continue
                else:
                    if int(childage) == age:
                        classpupils.append(existingdependant)
            except Exception:
                pass

    filename = 'FFCM CLASS ' +str(childage).upper()+' ('+str(len(classpupils)) +' PUPILS)'
    data = [
        ['LAST NAME', 'FIRST NAME',]
    ]
    childdetails =[]
    for child in classpupils:
        childdetails.append(child.c_surname)
        childdetails.append(child.c_firstname)
        data.append(childdetails)
        childdetails=[]
    return ExcelResponse(data, filename)



@login_required
def acceptparentage(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    parent = checkparent(allObject['member'])
    member = allObject['member']

    if request.method == 'POST':
        if parent:
            pass
        else:
            try:
                parent = chmodels.Parent.objects.get(member = allObject['member'])

            except ObjectDoesNotExist:
                parent = chmodels.Parent.objects.create(member = allObject['member'])
        member.private_number = make_password(request.POST.copy().get('private_number'))
        member.has_dependants=True
        member.save()
        existingdependants = chmodels.LraMembersChildren.objects.filter(parent_id=member.bio_data.member_id).exclude(del_flg='Y')
        if len(existingdependants) > 0:
 
            for existingdependant in existingdependants:
                try:
                    dateofbirth = datetime.datetime(existingdependant.c_date_of_birth.year,existingdependant.c_date_of_birth.month,existingdependant.c_date_of_birth.day)
                    agef = ((datetime.datetime.timestamp(datetime.datetime.now()) - datetime.datetime.timestamp(dateofbirth))/31556952)
                    age = datetime.datetime.now().year - dateofbirth.year
                    # age = math.ceil(agef)
                    if age >13:
                        continue
                    else:
                        try:
                            dependantexist = True
                            while dependantexist:
                                nums = '0123456789'
                                tempnums = ''
                                lalph = 'abcdefghijklmnopqrstuvwxyz'
                                templalph=''
                                ualph = lalph.upper()
                                tempualph = ''

                                for num in range(0,len(nums)):
                                    tempnums +=nums[round((random()-0.5)*len(nums))]
                                for num in range(0,len(lalph)):
                                    templalph +=lalph[round((random()-0.5)*len(lalph))]
                                for num in range(0,len(ualph)):
                                    tempualph +=ualph[round((random()-0.5)*len(ualph))]
                                firstletter= parent.member.user.first_name[0].upper()
                                lastletter =parent.member.user.last_name[0].upper()
                                temporary_userid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
                                userid= []
                                for char in temporary_userid:
                                    userid.insert(round(random()*5),char)
                                userid = ''.join(userid)
                                userid = 'CGCC'+userid
                                try:
                                    dependantmember = mmodels.Member.objects.get(memberid=userid)
                                except ObjectDoesNotExist:
                                    dependantmember=mmodels.Member.objects.create(dependant=True, user=parent.member.user,
                                    memberid=userid,bio_data=parent.member.bio_data,familyid=parent.member.familyid,
                                    full_name=existingdependant.c_firstname +' ' +existingdependant.c_surname)
                                    dependantexist = False

                                dependant = chmodels.Dependant.objects.create(bio_data=existingdependant, parent=parent.member, 
                                member = dependantmember)
                                firstletter= existingdependant.c_firstname[0].upper()
                                lastletter =existingdependant.c_firstname[len(existingdependant.c_firstname)-1].upper()
                                dependantid = firstletter+lastletter+parent.member.memberid 
                                dependant.dependantid=dependantid
                                dependant.save()
                                dependant.refresh_from_db()
                                # dateofbirth = datetime.datetime(dependant.date_of_birth.year,dependant.date_of_birth.month,dependant.date_of_birth.day)
                                # dependant.agef = ((datetime.datetime.timestamp(datetime.datetime.now()) - datetime.datetime.timestamp(dateofbirth))/31556952)
                                # dependant.age = math.ceil(dependant.agef)
                                parent.dependants.add(dependant)
                        except utils.IntegrityError:
                            continue
                except Exception:
                    pass
        template_name = 'children/parent.html'
        parent = chmodels.Parent.objects.get(member = allObject['member'])
        allObject['parent'] = parent  
        content = loader.render_to_string(template_name,allObject,request)
  
        output_data = {
                'content':content,
                        }
        return JsonResponse(output_data) 
    else:
        template_name = 'children/parentage_form.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'heading':'Accept Parentage'
                        }
        return JsonResponse(output_data)      


@login_required
def parenttab(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    parent = checkparent(allObject['member'])
    if parent:
        template_name = 'children/parent.html'
        parent = chmodels.Parent.objects.get(member = allObject['member'])
        allObject['parent'] = parent    
    else:
        template_name = 'children/not_parent_notice.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'content':content,
                    }
    return JsonResponse(output_data) 



@login_required
def eventtab(request, *args, **kwargs):
    # allObject = inherit(request, *args, **kwargs)
    # parent = checkparent(allObject['member'])
    # if parent:
    #     template_name = 'children/events.html'
    #     parent = chmodels.Parent.objects.get(member = allObject['member'])
    #     allObject['parent'] = parent
    #     upcomingevents =  list(mmodels.HostedEvent.objects.filter(end_date_time__gte = datetime.datetime.now(),open_to='children'))
    #     upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
    #     allObject['upcomingevents'] =upcomingevents  
    # else:
    #     template_name = 'children/not_parent_notice.html'
    # content = loader.render_to_string(template_name,allObject,request)
    # output_data = {
    #         'content':content,
    #                 }
    # return JsonResponse(output_data) 
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
    parent = checkparent(allObject['member'])
    if parent:
        template_name = 'children/home.html'
        parent = chmodels.Parent.objects.get(member = allObject['member'])
        allObject['parent'] = parent
        upcomingevents =  list(mmodels.HostedEvent.objects.filter(end_date_time__gte = datetime.datetime.now(),open_to='children'))
        upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
        allObject['upcomingevents'] =upcomingevents  
    else:
        template_name = 'children/not_parent_notice.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'content':content,
                    }
    return JsonResponse(output_data) 



@login_required
def changeavailabilitystatus(request,status=None, dependantid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    dependant = chmodels.Dependant.objects.get(dependantid=dependantid)
    if status =='False':
        status = True
        strstatus = 'Available'
    else:
        status = False
        strstatus = 'Not Available'
    dependant.available = status
    dependant.save()
    template_name = 'children/parent.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'done':True,
        'content':content,
        'modal_message':dependant.member.full_name +"'s"+ ' availability changed to <b>' +str(strstatus).capitalize() + '</b>'
                    }        
                    
    return JsonResponse(output_data)


@login_required
def changeguardianstatus(request,status=None, memberid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    guardian = chmodels.Guardian.objects.get(member__member_id=memberid)
    if status =='False':
        status = True
        strstatus = 'Active'
    else:
        status = False
        strstatus = 'Inactive'
    guardian.active = status
    guardian.save()
    template_name = 'children/parent.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'done':True,
        'content':content,
        'modal_message':(guardian.member.firstname + ' ' + guardian.member.surname).capitalize() +"'s"+ ' status changed to <b>' +str(strstatus).capitalize() + '</b>'
                    }        
                    
    return JsonResponse(output_data)



def changeregistrastionstatuschoice(request,eventid=None,dependantid=None, hostedeventid=None, action=None,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    allObject['action'] = action
    parent = allObject['parent']
    dependant = parent.dependants.get(available=True,member__memberid=dependantid)
    allObject['dependant'] = dependant
    template_name = 'children/choose_parent.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'heading':'Choose Approved Parent/Guardian',
        'modal_content':content,
                    }        
                    
    return JsonResponse(output_data)



def checkdepedantregistrations(parent,hostedevent):
    registrations = mmodels.Registration.objects.filter(attendee__dependant=True, attendee__familyid=parent.member.familyid, eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
    return registrations



@login_required
def changeregistrationstatus(request,status=None, memberid=None,dependantid=None, hostedeventid=None,eventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    teacher = allObject['teacher']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    dependantregistration = mmodels.Registration.objects.get(attendee__memberid=dependantid,eventid=eventid,hostedeventid=hostedeventid)
    dependantregistration.status=status
    parent = mmodels.Member.objects.get(user = dependantregistration.attendee.user,dependant=False)
    allObject['parent'] = parent    
    dependant = chmodels.Dependant.objects.get(member__memberid=dependantid )
    approvedmember =''
    try:
        approvedmember = mmodels.Member.objects.get(memberid = memberid).bio_data
    except ObjectDoesNotExist:
        approvedmember = mmodels.LraMembersBiodata.objects.get(member_id=memberid)
    if status == 'accredited':
        dependantregistration.accredited_by = member.bio_data.member_id
        dependantregistration.brought_in_by = approvedmember.member_id
    
    elif status == 'pickedup':
        if teacher:
            dependantregistration.checked_out_by = teacher.member.memberid
            dependantregistration.picked_by = approvedmember.member_id
            dependantregistration.save()

            subject = 'CGCC - Registration Status update'

            adminrecipientnumbers = []
            administrators = chmodels.Administrator.objects.filter(is_staff = True,can_receive_calls= True)
            for administrator in administrators:
                adminrecipientnumbers.append(administrator.member.bio_data.mobile1)  
            allObject['para1'] = 'Your dependant <b>' + dependant.member.full_name + '</b> has been picked up on ' + str(datetime.datetime.now()) +' by <b>' +approvedmember.lastname +' '+approvedmember.firstname + '</b>'
            allObject['para2'] = 'If you are not aware of this change, kindly contact any of the following numbers to report this <b>' + ' ,'.join(adminrecipientnumbers ) +'</b>'
            message = render_to_string('children/registration_status_update.html',allObject)
            email_from = settings.EMAIL_HOST_USER 
            recipient_list = []

            recipient_list.append(parent.user.email)
            try:
                send_mail( subject, message, email_from, recipient_list,html_message=message )
            except socket.gaierror:
                pass
            allObject['message'] = 'Dependant <b>' + dependant.member.full_name + '</b> has been picked up on ' + str(datetime.datetime.now())
            message = render_to_string('children/admin_registration_status_update.html',allObject)
            adminrecipientlist = []
            administrators = chmodels.Administrator.objects.filter(is_staff = True,can_receive_emails= True)
            for administrator in administrators:
                adminrecipientlist.append(administrator.member.user.email)
            try:
                send_mail( subject, message, email_from, adminrecipientlist,html_message=message)
            except socket.gaierror:
                pass
        else:
            subject ='CGCC - FFCM: Invalid Operation'
            email_from = settings.EMAIL_HOST_USER 
            allObject['message'] = 'Invalid <b> pickup operation <b> by <b>' + approvedmember.firstname +' '+approvedmember.surname +' </b> with contact details <br><b>' +approvedmember.mobile1 + ' and email address ' + approvedmember.email
            message = render_to_string('children/invalid_operation.html',allObject)
            adminrecipientlist = []
            administrators = chmodels.Administrator.objects.filter(is_staff = True,can_receive_emails= True)
            for administrator in administrators:
                adminrecipientlist.append(administrator.member.user.email)
            try:
                send_mail( subject, message, email_from, adminrecipientlist,html_message=message)
            except socket.gaierror:
                pass
            auth.logout(request)
            output_data ={
                    'modal_message':'You are not permitted to perform this operation',
                    'logout':True
                            }
            return JsonResponse(output_data)           
        
    member = allObject['member']    
    dependantregistration.save()

    # template_name = 'children/not_parent_notice.html'
    # content = loader.render_to_string(template_name,allObject,request)
    parent = chmodels.Parent.objects.get(member__user=dependantregistration.attendee.user)
    registrations = checkdepedantregistrations(parent,hostedevent)

    approvedregistrations = []
    allObject['parent'] = parent
    for registration in registrations:

        # for registration in registrations:
        #     registration.status = 'pickedup'
        #     registration.save()
        firstregistration = registration

        dependants = parent.dependants.all()
        approveddependants =[]
        for registration in registrations:
            if registration.status == 'accredited':
                for dependant in dependants:
                    if teacher:
                        if dependant.classid == teacher.classroom.classid:
                            if registration.attendee == dependant.member:
                                approvedregistrations.append(registration)
            elif registration.status == 'pickedup':
                approvedregistrations.append(registration)
            else:
                approvedregistrations.append(registration)

        break
    allObject['hostedevent'] = hostedevent
    allObject['registrations'] = approvedregistrations
    template_name = 'children/dependants_summary.html'
    updatecontent = loader.render_to_string(template_name,allObject,request)                 
    output_data ={
            'updatecontent':updatecontent,
            'modal_notification':'Status changed to <b>' +str(status).capitalize() + '</b>'
                    }
    return JsonResponse(output_data) 


def registerparentinline(parent,hostedevent):
    try:
        registration = mmodels.Registration.objects.get(attendee=parent.member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
        return False     
    except ObjectDoesNotExist:
        registration_id = hostedevent.initials+'00'+str(hostedevent.registrations.count()+1)+'-'+str(round(random()*1234567890))
        registration = mmodels.Registration.objects.create(registrationid=registration_id[0:8],attendee=parent.member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
        hostedevent.registrations.add(registration)
        if hostedevent.verification_steps == '0':
            registration.status = 'accredited'
            registration.accredited = True
            registration.verified = True
            registration.save()
        arrangeattendee(hostedevent,registration)
         
        return True


def gettrackingid():
    nums = '0123456789'
    tempnums = ''
    lalph = 'abcdefghijklmnopqrstuvwxyz'
    templalph=''
    ualph = lalph.upper()
    tempualph = ''

    for num in range(0,len(nums)):
        tempnums +=nums[round((random()-0.5)*len(nums))]
    for num in range(0,len(lalph)):
        templalph +=lalph[round((random()-0.5)*len(lalph))]
    for num in range(0,len(ualph)):
        tempualph +=ualph[round((random()-0.5)*len(ualph))]
    # firstletter= member.user.first_name[0].upper()
    # lastletter =member.user.last_name[0].upper()
    # temporary_trackingid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
    # trackingid= []
    # for char in temporary_trackingid:
    #     trackingid.insert(round(random()*5),char)
    # trackingid = ''.join(trackingid)
    trackingid=str(round(random()*1234567890))[0:6]
    return trackingid

                
def registerdependantinline(dependants,hostedevent,member,allObject):
    parent = chmodels.Parent.objects.get(member=member)
    trackingid = gettrackingid()      
    try:
        registrations = checkdepedantregistrations(parent,hostedevent)
        trackingidfound= False
        if len(registrations) >0:
            trackingid = registrations[0].trackingid
            trackingidfound = True
            allObject['trackingid'] = trackingid                 

        if len(dependants) > 0:
            for dependant in dependants:

                if dependant.classid == '' or dependant.groupid =='':
                    continue                
                classroom = chmodels.ClassRoom.objects.get(classid=dependant.classid)
                try:
                    classroomreg = chmodels.ClassRoomRegistration.objects.get(classid=classroom.classid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
                except ObjectDoesNotExist:
                    classroomreg = chmodels.ClassRoomRegistration.objects.create(classid=classroom.classid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
                classroomreg.refresh_from_db()
                regexist = True
    
                registrations = mmodels.Registration.objects.filter(trackingid=trackingid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid).exclude(attendee__user=parent.member.user,attendee__dependant=True).exclude(attendee__user=parent.parent_2.all()[0].user)
                if len(registrations) > 0:
                    registerdependantinline(dependants,hostedevent,member,allObject)
                else:
                    registration = mmodels.Registration.objects.create(registered_by=allObject['member'].bio_data.member_id, classid=classroom.classid, trackingid=trackingid, attendee=dependant.member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
                    regexist = False
                    registration.refresh_from_db()
                    trackingid=registration.trackingid
                    hostedevent.registrations.add(registration)
                    classroomreg.registrations.add(registration)
                    classroomreg.save()
                    if classroomreg in classroom.registrations.all():
                        pass
                    else:
                        classroom.registrations.add(classroomreg)
            # allObject['trackingid'] = trackingid                 

        
        return trackingid
    except IndexError:
        pass



@login_required
def pickupverification(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    output_data = {}
    teacher = allObject['teacher']
    template_name = 'children/dependants_summary.html'
    approvedregistrations = []
    def checkregistrations(secured):
        try:
            adultevent = mmodels.HostedEvent.objects.get(eventid=hostedevent.eventid,end_date_time__gte = datetime.datetime.now(),open_to='adults')
        except ObjectDoesNotExist:
            allObject['error'] = 'Child cannot be registered because parent have no event to attend'
            message = loader.render_to_string(template_name,allObject,request)
            output_data = {
                    'message':message,
                    'verified':True,
                            }
            return JsonResponse(output_data)
        try:
            parentregistration = mmodels.Registration.objects.get(attendee=parent.member,eventid=hostedevent.eventid,hostedeventid=adultevent.hostedeventid)
        except ObjectDoesNotExist:
            registerparentinline(parent,adultevent)
        registrations = checkdepedantregistrations(parent,hostedevent)
        registereddependants =[]
        for registration in registrations:
            registereddependants.append(registration.attendee)
        dependants =parent.dependants.all()
        canregister = []

        for dependant in dependants:
            if dependant.member not in registereddependants:
                if dependant.available and dependant.groupid !='':
                    canregister.append(dependant)
        if len(canregister) > 0:
            registerdependantinline(canregister,hostedevent,parent.member,allObject)
        registrations = checkdepedantregistrations(parent,hostedevent)
        for registration in registrations:
            if secured:
                registration.secured_search = True
                registration.save()
            else:
                registration.secured_search = False
                registration.save()
            if registration.status == 'accredited':
                for dependant in dependants:
                    if teacher:
                        if dependant.classid == teacher.classroom.classid:
                            if registration.attendee == dependant.member:
                                approvedregistrations.append(registration)
            elif registration.status == 'pickedup':
                approvedregistrations.append(registration)
            else:
                approvedregistrations.append(registration)
        allObject['registrations'] = approvedregistrations

    if request.method == 'POST':
        phonenumber = request.POST.copy().get('phonenumber')
        private_number = request.POST.copy().get('private_number')
        trackingid = request.POST.copy().get('trackingid')
        parentqrc = str(request.POST.copy().get('memberqrc'))

        if len(str(trackingid)) >5:
            registrations = mmodels.Registration.objects.filter(trackingid=trackingid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
            if len(registrations) >0:
                firstregistration = registrations[0]
                parent = chmodels.Parent.objects.get(member__user=firstregistration.attendee.user)            
                allObject['parent'] = parent
            approvedregistrations = []
            for registration in registrations:

                dependants = parent.dependants.all()
                for registration in registrations:
                    registration.secured_search = True
                    registration.save() 
                    if registration.status == 'accredited':
                        for dependant in dependants:
                            if teacher:
                                if dependant.classid == teacher.classroom.classid:
                                    if registration.attendee == dependant.member:
                                        approvedregistrations.append(registration)
                    elif registration.status == 'pickedup':
                        approvedregistrations.append(registration)
                    else:
                        approvedregistrations.append(registration)

                break
            allObject['registrations'] = approvedregistrations

            message = loader.render_to_string(template_name,allObject,request)
            output_data = {
                    'message':message,
                    'verified':True,
                            }
            return JsonResponse(output_data)
        elif len(str(parentqrc)) > 5:
            parentqrcdetails = parentqrc.split('-')
            try:
                allObject['qrc']=parentqrc
                parentmember = mmodels.Member.objects.get(memberid =parentqrcdetails[0])
                parent = chmodels.Parent.objects.get(member=parentmember)
                allObject['parent'] = parent
                try:
                    qrctimedifference = datetime.datetime.now() - datetime.datetime.fromtimestamp(float(parentqrcdetails[1]))
                    if qrctimedifference.total_seconds()/60 >= 5:
                        allObject['error'] = 'Expired QRCode'
                        message = loader.render_to_string(template_name,allObject,request)
                        output_data = {
                                'message':message,
                                'verified':True,
                                        }
                        return JsonResponse(output_data)
                    elif qrctimedifference.total_seconds()/60 < 0:
                        allObject['error'] = 'Call Security'
                        message = loader.render_to_string(template_name,allObject,request)
                        output_data = {
                                'message':message,
                                'verified':True,
                                        }
                        return JsonResponse(output_data)
                except ValueError:
                    allObject['error'] = 'Bad QRCode'
                    message = loader.render_to_string(template_name,allObject,request)
                    output_data = {
                                'message':message,
                                'verified':True,
                                        }
                    return JsonResponse(output_data)
        
                registerdependant = checkregistrations(True)

                registrations = checkdepedantregistrations(parent,hostedevent)
                approvedregistrations = []
                for registration in registrations:

                    dependants = parent.dependants.all()
                    for registration in registrations:
                        registration.secured_search = True
                        registration.save() 
                        if registration.status == 'accredited':
                            for dependant in dependants:
                                if teacher:
                                    if dependant.classid == teacher.classroom.classid:
                                        if registration.attendee == dependant.member:
                                            approvedregistrations.append(registration)
                        elif registration.status == 'pickedup':
                            approvedregistrations.append(registration)
                        else:
                            approvedregistrations.append(registration)

                    break
                allObject['registrations'] = approvedregistrations
                message = loader.render_to_string(template_name,allObject,request)                 
                output_data ={
                        'message':message,
                        'verified':False,
                                }
                return JsonResponse(output_data)

            except ObjectDoesNotExist:
                allObject['error'] = 'Parent Not Found'
                allObject['registrations'] = False
                message = loader.render_to_string(template_name,allObject,request)        
                output_data = {
                        'message':message,
                        'verified':False,
                                }
                return JsonResponse(output_data)

        elif len(str(phonenumber)) > 10 and len(str(private_number)) ==0:
            try:
                parent = chmodels.Parent.objects.get(member__bio_data__mobile1=phonenumber)
            except ObjectDoesNotExist:
                try:
                    parent = chmodels.Parent.objects.get(member__bio_data__email=phonenumber)            
                except ObjectDoesNotExist:
                    allObject['error'] = 'Parent not found'
                    allObject['registrations'] = False
                    message = loader.render_to_string(template_name,allObject,request)        
                    output_data={
                            'message':message,
                            'verified':False,
                                    }
                    return JsonResponse(output_data)
            allObject['parent'] = parent
            registerdependant = checkregistrations(False)

            registrations = checkdepedantregistrations(parent,hostedevent)

            allObject['registrations'] = registrations
            message = loader.render_to_string(template_name,allObject,request)                 
            output_data ={
                    'message':message,
                            }
            return JsonResponse(output_data)

        elif len(str(phonenumber)) > 10 and len(str(private_number)) > 4:
            
            try:
                member = mmodels.Member.objects.get(bio_data__mobile1=phonenumber,dependant=False)
            except ObjectDoesNotExist:
                try:
                    member = mmodels.Member.objects.get(bio_data__email=phonenumber,dependant=False)
                except ObjectDoesNotExist:
                        allObject['error'] = 'Parent not found'
                        allObject['registrations'] = False
                        message = loader.render_to_string(template_name,allObject,request)        
                        output_data={
                                'message':message,
                                'verified':False,
                                        }
                        return JsonResponse(output_data)
            passwordcheck = check_password(str(private_number),str(member.private_number))

            if passwordcheck:
                parent = chmodels.Parent.objects.get(member = member)
                allObject['parent'] = parent
                registrations = checkdepedantregistrations(parent,hostedevent)
                approvedregistrations = []
                for registration in registrations:

                    dependants = parent.dependants.all()
                    for registration in registrations:
                        registration.secured_search = True
                        registration.save() 
                        if registration.status == 'accredited':
                            for dependant in dependants:
                                if teacher:
                                    if dependant.classid == teacher.classroom.classid:
                                        if registration.attendee == dependant.member:
                                            approvedregistrations.append(registration)
                        elif registration.status == 'pickedup':
                            approvedregistrations.append(registration)
                        else:
                            approvedregistrations.append(registration)

                    break
                allObject['registrations'] = approvedregistrations
                message = loader.render_to_string(template_name,allObject,request)                 
                output_data ={
                        'message':message,
                        'verified':False,
                                }
                return JsonResponse(output_data)
            else:
                allObject['error'] = 'Incorrect Private Number'
                allObject['registrations'] = False
                message = loader.render_to_string(template_name,allObject,request)        
                output_data={
                        'message':message,
                        'verified':False,
                                }
                return JsonResponse(output_data)


    allObject['hostedevent'] = hostedevent
    if member.user.is_staff:
        template_name = 'children/pickup_verification.html'
        parent = chmodels.Parent.objects.get(member = allObject['member'])
        allObject['parent'] = parent
        upcomingevents =  list(mmodels.HostedEvent.objects.filter(start_date_time__gt = datetime.datetime.now()))
        upcomingevents.sort(key=lambda x: x.start_date_time,reverse=True)
        allObject['upcomingevents'] =upcomingevents  
    else:
        return redirect('children_dashboard')
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'content':content,
                    }
    return render(request,template_name,allObject)
    return JsonResponse(output_data) 

import socket
import math
def assigngroup(dependant):
    try:
        group = chmodels.Group.objects.get(age = dependant.age)
        group.pupils.add(dependant)
        dependant.currentclass = group.name
        dependant.groupid = group.groupid
        for classroom in group.classrooms.all():
            if classroom.full:
                pass
            else:
                dependant.currentclass = classroom.classid
                classroom.pupils.add(dependant)
        dependant.save()
    except ObjectDoesNotExist:
        pass
    return True



def registerdependentchoice(request,eventid=None,hostedeventid=None,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent
    parent =  allObject['parent']
    dependants =parent.dependants.filter(available=True).exclude(classid='',groupid='')
    dependantmembers = []
    for dependant in dependants:
        dependantmembers.append(dependant.member)
    registered = []
    nonregistered=[]
    registereddependants =[]
    registrations = checkdepedantregistrations(parent,hostedevent)
    if len(registrations) >0:
        trackingid = registrations[0].trackingid
        allObject['trackingid'] = trackingid
        for registration in registrations:
            registereddependants.append(registration.attendee)
            if registration.attendee in dependantmembers:
                registered.append(registration.attendee)
    for dependantmember in dependantmembers:
        if dependantmember in registereddependants:
            pass
        else:
            nonregistered.append(dependantmember)
    allObject['registrations'] = registrations
    allObject['registered'] = registered
    allObject['dependants'] = dependantmembers

    allObject['registereddependants'] = registereddependants
    allObject['nonregistered'] = nonregistered
    allObject['allregistrations'] = registrations
    template_name = 'children/register_dependants.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'heading':'Register Dependant(s)',
        'modal_content':content,
                    }        
                    
    return JsonResponse(output_data)




@login_required
def registeralldependants(request,eventid=None,hostedeventid=None,phonenumber=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    allObject['hostedevent'] = hostedevent 
    try:
        parent = chmodels.Parent.objects.get(member__bio_data__mobile1=phonenumber)
        allObject['parent'] = parent
        try:
            adultevent = mmodels.HostedEvent.objects.get(eventid=hostedevent.eventid,end_date_time__gte = datetime.datetime.now(),open_to='adults')
        except ObjectDoesNotExist:
            error = 'Child cannot be registered because parent have no event to attend'
            output_data = {
                    'modal_notification':error,
                    'verified':True,
                            }
            return JsonResponse(output_data)
        try:
            parentregistration = mmodels.Registration.objects.get(attendee=parent.member,eventid=hostedevent.eventid,hostedeventid=adultevent.hostedeventid)
        except ObjectDoesNotExist:
            registerparentinline(parent,adultevent)
        registrations = checkdepedantregistrations(parent,hostedevent)
        registereddependants =[]
        for registration in registrations:
            registereddependants.append(registration.attendee)
        dependants =list(parent.dependants.all())
        if len(registereddependants) == len(dependants):
            pass
        else:
            canregister = []
            for dependant in dependants:
                if dependant.member not in registereddependants:
                    if dependant.available and dependant.classid and dependant.groupid:
                        canregister.append(dependant)
            trackingid= registerdependantinline(canregister,hostedevent,parent.member,allObject)
        # registrations = mmodels.Registration.objects.filter(attendee__user=parent.member.user,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)               
        allObject['hostedevent']=hostedevent
        template_name = 'children/success.html'
        try:
            allObject['message'] = 'Registration successful <br> Tracking ID <br> <p class="h1"> ' + trackingid +'</p>'
        except UnboundLocalError:
            allObject['message'] = 'Registration failed'
        successmessage = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'modal_message':successmessage,
                        }        
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        allObject['registrations'] = False
        template_name = 'children/dependants_summary.html'
        message = loader.render_to_string(template_name,allObject,request)        
        output_data ={
                'message':message,
                'verified':False,
                        }
        return JsonResponse(output_data)

    
@login_required
def registerdependant(request,eventid=None,hostedeventid=None,memberid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    event = mmodels.Event.objects.get(eventid=eventid)
    dependant = chmodels.Dependant.objects.get(member__memberid=memberid)
    canregister =[]
    if not dependant.available:
        message ='Dependant is currently not available for registration'
        output_data = {
        'modal_notification':message,
                }
        return JsonResponse(output_data)
    canregister.append(dependant)

    try:
        parent = chmodels.Parent.objects.get(member__bio_data__mobile1=dependant.parent.bio_data.mobile1)
    except ObjectDoesNotExist:
        parent = chmodels.Parent.objects.get(member__email=dependant.parent.email)

    allObject['parent'] = parent
    try:
        adultevent = mmodels.HostedEvent.objects.get(eventid=hostedevent.eventid,end_date_time__gte = datetime.datetime.now(),open_to='adults')
    except ObjectDoesNotExist:
        error = 'Child cannot be registered because parent have no event to attend'
        output_data = {
                'modal_notification':error,
                'verified':True,
                        }
        return JsonResponse(output_data)
    try:
        parentregistration = mmodels.Registration.objects.get(attendee=parent.member,eventid=hostedevent.eventid,hostedeventid=adultevent.hostedeventid)
    except ObjectDoesNotExist:
        registerparentinline(parent,adultevent)
    try:
        registration = mmodels.Registration.objects.get(attendee=dependant.member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
        message ='Dependant already registered'
        output_data = {
        'header':hostedevent.title,
        'message':message,
        'registered':True,
                }
        return JsonResponse(output_data) 
    except ObjectDoesNotExist:
        trackingid = registerdependantinline(canregister,hostedevent,member,allObject)
        # registrations = checkdepedantregistrations(parent,hostedevent)
        # if len(registration) >0:
        #     trackingid = registration[0].trackingid
        # else:
        #     trackingid = gettrackingid()

        # try:
        #     classroom = chmodels.ClassRoom.objects.get(classid=dependant.classid)
        # except ObjectDoesNotExist:
        #     message =dependant.member.full_name+ ' does not belong to any Group. <br> <b>Make sure his/her date of birth is currectly set</b>'
        #     output_data = {
        #     'modal_notification':message,
        #             }
        #     return JsonResponse(output_data) 
        # try:
        #     classroomreg = chmodels.ClassRoomRegistration.objects.get(classid=classroom.classid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
        # except ObjectDoesNotExist:
        #     classroomreg = chmodels.ClassRoomRegistration.objects.create(classid=classroom.classid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
        # classroomreg.refresh_from_db()
        # regexist = True
        # while regexist:
        #     trackingid = gettrackingid()
        #     try:        
        #         registration = mmodels.Registration.objects.get(trackingid=trackingid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
        #     except ObjectDoesNotExist:
        #         registration = mmodels.Registration.objects.create(classid=classroom.classid, trackingid=trackingid, attendee=dependant.member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
        #         regexist = False
        #     hostedevent.registrations.add(registration)
        #     classroomreg.registrations.add(registration)
        #     classroom.registrations.add(classroomreg)
        #     # if member.user.is_staff :
        #     #     registration.refresh_from_db()
        #     #     registration.accredited = True
        #     #     registration.save()
        
    
        hostedevent.save()
        hostedevent.refresh_from_db()
    errors = updateeventstatus(hostedevent)
    allObject['hostedevent']=hostedevent
    template_name = 'children/success.html'
    allObject['message'] = 'Registration successful <br> Tracking ID <br> <p class="h1"> ' + trackingid +'</p>'
    successmessage = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'modal_message':successmessage,
                    }        
    return JsonResponse(output_data)



@login_required
def unregisterdependant(request,eventid=None,hostedeventid=None,memberid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    event = mmodels.Event.objects.get(eventid=eventid)
    dependant = chmodels.Dependant.objects.get(member__memberid=memberid)
    try:
        registration = mmodels.Registration.objects.get(attendee__memberid=dependant.member.memberid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
        if registration.status == 'accredited' or registration.status == 'pickedup':
            message =dependant.member.full_name +' cannot be unregistered'
            output_data = {
            'modal_notification':message,
                    }
            return JsonResponse(output_data) 
        registration.delete()
        message =dependant.member.full_name +' has been unregistered'
        output_data = {
        'modal_notification':message,
                }
        return JsonResponse(output_data) 
    except ObjectDoesNotExist:
        message =dependant.member.full_name +' is not registered for this event'
        output_data = {
        'modal_notification':message,
                }
        return JsonResponse(output_data) 



def editdependant(request,dependantid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    dependant = chmodels.Dependant.objects.get(dependantid=dependantid)
    child = dependant.bio_data
    if request.method == 'POST':
        parent = chmodels.Parent.objects.get(member__memberid=dependant.parent.memberid)
        allObject['parent'] = parent
        dependantimage = chforms.DependantImage(request.POST, request.FILES,instance=dependant)
        childform = chforms.AddChild(request.POST,instance=child)
        if childform.is_valid:
            childform.save()
            child = childform.instance
            child.refresh_from_db()
            # dependant = chmodels.Dependant.objects.create(parent=parent.member, care = str(request.POST.copy().get('special_care')),parentid=parent.member.memberid, first_name = str(request.POST.copy().get('first_name')),last_name = str(request.POST.copy().get('last_name')),date_of_birth=request.POST.copy().get('date_of_birth'))
            # dependant.refresh_from_db()
            # dateofbirth = datetime.datetime(child.c_date_of_birth.year,child.c_date_of_birth.month,child.c_date_of_birth.day)
            # dependant.agef = ((datetime.datetime.timestamp(datetime.datetime.now()) - datetime.datetime.timestamp(dateofbirth))/31556952)
            # dependant.age = math.ceil(dependant.agef)
            dateofbirth = str(request.POST.copy().get('c_date_of_birth'))
            dateofbirthobj = datetime.datetime.strptime(dateofbirth, '%Y-%m-%d')
            if datetime.datetime.now().year-dateofbirthobj.year > 13:
                dependant.classid=''
                dependant.groupid=''
                dependant.classname=''
                dependant.groupname = ''
            dependant.save()
            dependantimage.save()
            assignedgroup = assigngroup(dependant)
            parent.save()

            template_name = 'general/success.html'
            message = "Dependant "+ str(dependant.bio_data) +' was edited successfully'
            allObject['message'] = message
            successcontent = loader.render_to_string(template_name,allObject,request)
            template_name = 'children/parent.html'
            content = loader.render_to_string(template_name,allObject,request)
            output_data = {
                'done':True,
                'content':content,
                'modal_message':successcontent,
                            }        
                            
            return JsonResponse(output_data)
        else:
            allObject['dependant']=dependant
            template_name = 'children/edit_dependant.html'
            content = loader.render_to_string(template_name,allObject,request)
            output_data = {
                'heading':'Edit Dependant',
                'modal_content':content,
                'notification':dependant.errors
                            }        
                            
            return JsonResponse(output_data)
    else:
        allObject['dependant']=dependant
        template_name = 'children/edit_dependant.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'heading':'Edit Dependant',
            'modal_content':content,
                        }        
                        
        return JsonResponse(output_data)



def addparent(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    if request.method == 'POST':
        member = allObject['member']
        parent = chmodels.Parent.objects.get(member = allObject['member'])
        password = str(request.POST.copy().get('password'))
        password_is_correct = check_password(password,member.user.password)
        if password_is_correct:
            identifier =str(request.POST.copy().get('identifier'))
            try:
                parent2 = mmodels.Member.objects.get(bio_data__mobile1=identifier,dependant=False)
                parent2 = chmodels.Parent.objects.get(member=parent2)
            except ObjectDoesNotExist:
                try:
                    parent2 = mmodels.Member.objects.get(bio_data__email=identifier)
                    parent2 = chmodels.Parent.objects.get(member=parent2)

                except ObjectDoesNotExist:
                    output_data = {
                    'modal_message':'Member with detail <b>' + identifier +' </b> has not been profiled as parent. Kindly ask him/her to signup here as a parent and try again.'
                                }        
                                
                    return JsonResponse(output_data)
            if parent2.member.bio_data.gender == member.bio_data.gender:
                output_data = {
                    'modal_message':'Member of the same gender cannot be added as Parent.'
                                }        
                                
                return JsonResponse(output_data)

            elif parent2.member.bio_data.surname != member.bio_data.surname:
                output_data = {
                    'modal_message':'Only member of the same surname can be added as Parent.'
                                }        
                                
                return JsonResponse(output_data)
            parent.parent_2.clear()
            parent.parent_2.add(parent2.member)
            parent.save()
            parent2.member.familyid = member.familyid
            parent2.member.save()
            output_data = {
                'modal_message':'Parent <b>'+parent2.member.bio_data.firstname + ' ' + parent2.member.bio_data.surname + '</b> was added successfully'
                            }        
                            
            return JsonResponse(output_data)
                  
        else:
            member.suspension_count += 1
            member.save()

            if member.suspension_count > 2:
                output_data = {
                'logout':True,
                'modal_message':'<p><b> Your account has been temporarily suspended and you will be logged out now</b></p>'
                            }        
                            
                return JsonResponse(output_data)
            output_data = {
                'heading':'Edit Dependant',
                'modal_message':'Invalid Password <br> <p class="text-danger"> <b> You have ' + str(3-member.suspension_count) + ' times to retry </b></p>'
                            }        
                            
            return JsonResponse(output_data)
    else:
        # allObject['password']=password
        template_name = 'children/add_parent.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'heading':'Change Private Change',
            'modal_content':content,
                        }        
                        
        return JsonResponse(output_data)


def addguardian(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    if request.method == 'POST':
        member = allObject['member']
        parent = chmodels.Parent.objects.get(member = allObject['member'])
        password = str(request.POST.copy().get('password'))
        password_is_correct = check_password(password,member.user.password)
        if password_is_correct:
            identifier =str(request.POST.copy().get('identifier'))
            try:
                guardian = mmodels.LraMembersBiodata.objects.get(mobile1=identifier)
            except ObjectDoesNotExist:
                try:
                    guardian = mmodels.LraMembersBiodata.objects.get(email=identifier)
                except ObjectDoesNotExist:
                    output_data = {
                    'modal_message':'Member with detail <b>' + identifier +' </b> does not exist on church database. Try again '
                                }        
                                
                    return JsonResponse(output_data)
            try:
                existingguardian = chmodels.Guardian.objects.get(member = guardian)
                output_data = {
                'modal_message':'Guardian already exist'
                            }        
                            
                return JsonResponse(output_data)
            except ObjectDoesNotExist:
                newguardian = chmodels.Guardian.objects.create(member = guardian)
                parent.guardians.add(newguardian) 
                parent.save()
            output_data = {
                'modal_message':'Guardian <b>'+guardian.firstname + ' ' + guardian.surname + '</b> was added successfully'
                            }        
                            
            return JsonResponse(output_data)
                  
        else:
            member.suspension_count += 1
            member.save()

            if member.suspension_count > 2:
                output_data = {
                'logout':True,
                'modal_message':'<p><b> Your account has been temporarily suspended and you will be logged out now</b></p>'
                            }        
                            
                return JsonResponse(output_data)
            output_data = {
                'heading':'Edit Dependant',
                'modal_message':'Invalid Password <br> <p class="text-danger"> <b> You have ' + str(3-member.suspension_count) + ' times to retry </b></p>'
                            }        
                            
            return JsonResponse(output_data)
    else:
        # allObject['password']=password
        template_name = 'children/add_guardian.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'heading':'Change Private Change',
            'modal_content':content,
                        }        
                        
        return JsonResponse(output_data)




def changeprivatenumber(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    member = allObject['member']
    if request.method == 'POST':
        password = str(request.POST.copy().get('password'))
        password_is_correct = check_password(password,member.user.password)
        if password_is_correct:
            member.private_number = make_password(request.POST.copy().get('private_number'))
            member.save()
            output_data = {
                'modal_message':'Your Private Number was changed successfully'
                            }        
                            
            return JsonResponse(output_data)
        else:
            member.suspension_count += 1
            member.save()

            if member.suspension_count > 2:
                output_data = {
                'logout':True,
                'modal_message':'<p><b> Your account has been temporarily suspended and you will be logged out now</b></p>'
                            }        
                            
                return JsonResponse(output_data)
            output_data = {
                'heading':'Edit Dependant',
                'modal_message':'Invalid Password <br> <p class="text-danger"> <b> You have ' + str(3-member.suspension_count) + ' times to retry </b></p>'
                            }        
                            
            return JsonResponse(output_data)
    else:
        # allObject['password']=password
        template_name = 'children/change_private_number.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'heading':'Change Private Change',
            'modal_content':content,
                        }        
                        
        return JsonResponse(output_data)




def adddependant(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    if request.method == 'POST':
        parent = chmodels.Parent.objects.get(member = allObject['member'])
        allObject['parent'] = parent
        member = allObject['member']
        try:       
            dependantmember = mmodels.Member.objects.get(user=parent.member.user,dependant=True,
            full_name__contains=request.POST.copy().get('c_firstname'))
            output_data = {
            'modal_message':'Dependant already added',       
            }        
                    
            return JsonResponse(output_data)
        except ObjectDoesNotExist:
            dateofbirth = str(request.POST.copy().get('c_date_of_birth'))
            dateofbirthobj = datetime.datetime.strptime(dateofbirth, '%Y-%m-%d')
            if datetime.datetime.now().year-dateofbirthobj.year > 13:
                output_data = {
                'modal_notification':"Dependant's age is more than 13 years and cannot be added",       
                }        
                    
                return JsonResponse(output_data)
            child = chforms.AddChild(request.POST)
            if child.is_valid:
                child.save()
                child=child.instance
                child.parent_id = member.bio_data.member_id
                child.member_id = member.bio_data.member_id
                child.save()
                child.refresh_from_db()                
                # dependant = chforms.AddDependant(request.POST)
                # if dependant.is_valid:
                # dependant.save(commit=False)
                # dependant.bio_data = child
                exist = True
                while exist:
                    nums = '0123456789'
                    tempnums = ''
                    lalph = 'abcdefghijklmnopqrstuvwxyz'
                    templalph=''
                    ualph = lalph.upper()
                    tempualph = ''

                    for num in range(0,len(nums)):
                        tempnums +=nums[round((random()-0.5)*len(nums))]
                    for num in range(0,len(lalph)):
                        templalph +=lalph[round((random()-0.5)*len(lalph))]
                    for num in range(0,len(ualph)):
                        tempualph +=ualph[round((random()-0.5)*len(ualph))]
                    firstletter= parent.member.user.first_name[0].upper()
                    lastletter =parent.member.user.last_name[0].upper()
                    temporary_userid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
                    userid= []
                    for char in temporary_userid:
                        userid.insert(round(random()*5),char)
                    userid = ''.join(userid)
                    userid = 'CGCC'+userid
                    try:
                        dependantmember = mmodels.Member.objects.get(memberid=userid)
                    except ObjectDoesNotExist:
                        dependantmember=mmodels.Member.objects.create(dependant=True,familyid= parent.member.familyid,bio_data=parent.member.bio_data, user=parent.member.user,
                        memberid=userid,
                        full_name=child.c_firstname +' ' +child.c_surname)
                        exist = False
                dependant = chmodels.Dependant.objects.create(bio_data=child,parent=parent.member,member= dependantmember)
                dependant.refresh_from_db()
                firstletter= child.c_firstname[0].upper()
                lastletter =child.c_firstname[len(child.c_firstname)-1].upper()
                dependantid = firstletter+lastletter+parent.member.memberid 
                dependant.dependantid=dependantid
                dateofbirth = datetime.datetime(dependant.bio_data.c_date_of_birth.year,dependant.bio_data.c_date_of_birth.month,dependant.bio_data.c_date_of_birth.day)
                dependant.agef = ((datetime.datetime.timestamp(datetime.datetime.now()) - datetime.datetime.timestamp(dateofbirth))/31556952)
                dependant.age = math.ceil(dependant.agef)
                parent.dependants.add(dependant)
                parent.save()
                dependant.save()
                dependantimage = chforms.DependantImage(request.POST, request.FILES,instance=dependant)
                dependantimage.save()
                assignedgroup = assigngroup(dependant)
                template_name = 'general/success.html'
                message = "Dependant "+dependant.bio_data.c_firstname + ' '+dependant.bio_data.c_surname +' was added successfully'
                allObject['message'] = message
                successcontent = loader.render_to_string(template_name,allObject,request)
                template_name = 'children/parent.html'
                content = loader.render_to_string(template_name,allObject,request)
                output_data = {
                    'done':True,
                    'content':content,
                    'modal_message':successcontent,
                                }        
                                
                return JsonResponse(output_data)
            
                # else:
                #     template_name = 'children/add_dependant.html'
                #     content = loader.render_to_string(template_name,allObject,request)
                #     output_data = {
                #         'heading':'Add Dependant',
                #         'modal_content':content,
                #                     }        
                                    
                #     return JsonResponse(output_data)
    else:
        # allObject['password']=password
        template_name = 'children/add_dependant.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'heading':'Add Dependant',
            'modal_content':content,
                        }        
                        
        return JsonResponse(output_data)


@login_required
def myevents(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'children/my_events.html'
    member = allObject['member']
    events = list(chmodels.Event.objects.filter(host=member))
    events.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['myevents'] =events
    return render(request,template_name,allObject)

@login_required
def updateprofileform(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'children/update_profile.html'
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
    template_name = 'children/event_qrcode.html'
    allObject['qrc_options'] =QRCodeOptions(hostedevent.hostedeventid,size='18', border=8, error_correction='L',image_format='png', )
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
            'modal_content':content,
            'heading':hostedevent.title,
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
    template_name = 'children/event_qrcode.html'
    context = dict(
            qrc_options= QRCodeOptions(registration.registrationid,size='18', border=8, error_correction='L',image_format='png', ),
        )
    content = loader.render_to_string(template_name,context,request)
    output_data = {
            'modal_content':content,
            'header':hostedevent.title,
                    }
    return JsonResponse(output_data)  



@login_required
def attendeeqrcverification(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    qrcodeid = request.GET.get('eventid')
    member = allObject['member']      
    allObject['hostedevent'] = hostedevent
    if hostedevent.one_day:
        if qrcodeid == hostedevent.hostedeventid:
            registration = mmodels.Registration.objects.get(attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,day=False)
            if hostedevent.verification_steps != '2':
                registration.verified = True
                registration.completed = True
                registration.save()
            else:
                registration.verified = True
                registration.save()          
            if hostedevent.one_time_ticketing and hostedevent.one_time_arrangement:
                for ticket in hostedevent.tickets.all():
                    if registration in ticket.registrations.all():
                        registration.seat_number=arrangeattendee(ticket,hostedevent,registration)
                        registration.save()            

            template_name = 'children/success.html'
            allObject['message'] = 'Welcome to ' + hostedevent.title
            message = loader.render_to_string(template_name,allObject,request)
            template_name = 'children/attendee_event_manager.html'
            content = loader.render_to_string(template_name,allObject,request)
            output_data = {
                    'header':hostedevent.title,
                    'message':message,
                    'attended':True,
                    'content':content
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
                                    tickets = chmodels.EventTicket.objects.filter(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)

                    template_name = 'children/success.html'
                    allObject['message'] = 'Welcome to ' + hostedevent.title +' day '+ eventday.day
                    message = loader.render_to_string(template_name,allObject,request)
                    template_name = 'children/attendee_event_manager.html'
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
        
    input_data = str(hostedevent.eventid)
    template_name = 'children/event_qrcode.html'
    context = dict(
            qrc_options= QRCodeOptions(hostedevent.eventid,size='18', border=8, error_correction='L',image_format='png', ),
        )
    content = loader.render_to_string(template_name,context,request)
    output_data = {
            'modal_content':content,
            'header':hostedevent.title,
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
        tickets = chmodels.EventTicket.objects.filter(eventid=hostedevent.eventid)
        for eventticket in tickets:
            for eventregistration in eventticket.registrations.all():
                if registration == eventregistration:
                    ticket=eventticket
                    allObject['ticket']=ticket
        template_name = 'children/attendee_summary.html'
        message = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'message':message,
                'verified':True,
                        }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        allObject['registration'] = False
        template_name = 'children/attendee_summary.html'
        message = loader.render_to_string(template_name,allObject,request)        
        output_data = {
                'message':message,
                'verified':False,
                        }
        return JsonResponse(output_data)


@login_required
def viewevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'children/view_event.html'  
    member = allObject['member']            
    event = chmodels.Event.objects.get(host=member, eventid=eventid)
    # hostedevents = mmodels.HostedEvent.objects.filter(eventid=hostedevent.eventid)
    allObject['event'] = event
    # allObject['hostedevents'] = hostedevents

    allObject['attendeescount'] = mmodels.Registration.objects.filter(eventid=eventid,verified=True).count()
    return render(request,template_name,allObject)


@login_required
def manageevent(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'children/manage_event.html'        
    event = chmodels.Event.objects.get(eventid=eventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    if not hostedevent.one_day:
        if hostedevent.days.count() > 0:
            for eventday in hostedevent.days.all():
                updateeventday(eventday)
    updateeventstatus(hostedevent)
    hostedevent.refresh_from_db()
    daytickets = chmodels.EventTicket.objects.filter(eventid=eventid,hostedeventid=hostedeventid,day=True)
    allObject['daytickets'] = daytickets
    dayarrangements = chmodels.Arrangement.objects.filter(eventid=eventid,hostedeventid=hostedeventid,day=True)
    allObject['dayarrangements'] = dayarrangements
    allObject['event'] = event
    allObject['hostedevent'] = hostedevent
    allObject['attendeescount'] = mmodels.Registration.objects.filter(eventid=hostedevent.eventid,verified=True).count()
    return render(request,template_name,allObject)




@login_required
def deleteeventday(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    day = chmodels.EventDay.objects.get(eventid=eventid,hostedeventid=hostedeventid,dayid=dayid)
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
        eventday = chmodels.EventDay.objects.get(dayid=dayid, eventid=eventid,hostedeventid=hostedeventid) 
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
                hostedeventtickets = chmodels.EventTicket.objects.filter(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
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
                    template_name = 'children/success.html'
                    allObject['message'] = 'Congratulations! You have registered for ' + registered['eventtitle']
                    message = loader.render_to_string(template_name,allObject,request)
                    template_name = 'children/attendee_event_manager.html'
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
                        template_name = 'children/success.html'
                        allObject['message'] = 'Congratulations! You have registered for ' + registered['eventtitle']
                        message = loader.render_to_string(template_name,allObject,request)
                        template_name = 'children/attendee_event_manager.html'
                        return attendeemanager(request,hostedevent,message)

                


@login_required
def eventdaydetails(request,eventid=None,hostedeventid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    eventday = chmodels.EventDay.objects.get(dayid=dayid, eventid=eventid,hostedeventid=hostedeventid) 
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
    event_details_template = 'children/event_day_details.html'
    event_details = loader.render_to_string(event_details_template,allObject,request)
    output_data = { 
                    'modal_content':event_details,
                    'heading':eventday.title
                }
    return JsonResponse(output_data) 

    
@login_required
def eventdetails(request,eventid=None,hostedeventid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'children/event_details.html'  
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
    template_name = 'children/attendee_event_manager.html'
    content = loader.render_to_string(template_name,allObject,request)
    ticketbtn = 'children/ticket_btn.html'
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
    if member.profile_updated:
        hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
        if checkeventstatus(hostedevent):
            allObject['hostedevent'] = hostedevent
            if hostedevent.days.count() > 0:
                return eventdays(request,hostedevent)
            if hostedevent.one_time_ticketing:
                if checkticket(request,hostedevent):
                    return buyticket(request,hostedevent)
            elif hostedevent.one_time_arrangement:
                registration_id = hostedevent.initials+'00'+str(hostedevent.registrations.count()+1)+'-'+str(round(random()*1234567890))
                registration = mmodels.Registration.objects.create(registrationid=registration_id[0:8],attendee=member,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
                hostedevent.registrations.add(registration)
                if arrangeattendee(hostedevent,registration) == 'No space':
                    registration.delete()
                    message = 'Sorry, there is no more space for registration'
                    output_data = {
                            
                            'modal_message':message,
                                    }
                    return JsonResponse(output_data) 
            updateeventstatus(hostedevent)
            allObject['hostedevent']=hostedevent
            template_name = 'children/success.html'
            allObject['message'] = 'Congratulations! You have registered for ' + hostedevent.title
            message = loader.render_to_string(template_name,allObject,request)
            template_name = 'children/attendee_event_manager.html'
            return attendeemanager(request,hostedevent,message)
        else:
            allObject['hostedevent']=hostedevent
            message = 'Event not available'
            return attendeemanager(request,hostedevent,message)            
        
    else:
        return updateprofileform(request, *args, **kwargs)



@login_required
def eventdays(request,hostedevent, *args, **kwargs):
    allObject = inherit(request)
    member = allObject['member']
    allObject['hostedevent'] = hostedevent
    registration_full = True
    
    template_name = 'children/event_days.html'
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
    template_name = 'children/buy_ticket.html'
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
           


def registerattendee(allObject,hostedevent,dayid,ticket=None):
    registration_id = hostedevent.initials+'00'+str(hostedevent.registrations.count()+1)+'-'+str(round(random()*1234567890))
    registration = mmodels.Registration.objects.create(registrationid=registration_id[0:8],attendee=allObject['member'],eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid)
    hostedevent.registrations.add(registration)
    if ticket == None:
        pass
    else:
        ticket.registrations.add(registration)
        ticket.save()
    # hostedevent.attendees.add(member)
    hostedevent.save()
    hostedevent.refresh_from_db()
    registration.ticketid = ticket.ticketid
    registration.save()
    if hostedevent.verification_steps == '0':
        registration.verified = True
        registration.completed = True
        registration.save() 
        if hostedevent.one_day:
            if hostedevent.one_time_ticketing and hostedevent.one_time_arrangement:
                registration.seat_number=arrangeattendee(ticket,hostedevent,registration)
                registration.save()
                return {'eventtitle':hostedevent.title,'registered':True}

        elif not hostedevent.one_day and hostedevent.one_time_ticketing:
            if len(dayid) > 5:
                eventday = chmodels.EventDay.objects.get(dayid=dayid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
                if eventday.ticket_required and eventday.arrange:
                    registration.seat_number=arrangeattendee(ticket,hostedevent,registration)
                    registration.day= True
                    registration.dayid= dayid
                    registration.save()
                    eventday.registrations.add(registration)
                    eventday.save()
                    eventtitle = eventday.title +' DAY ' + str(eventday.day)
                    return {'eventtitle':eventtitle,'registered':True}
        elif not hostedevent.one_day and not hostedevent.one_time_ticketing:
            eventday = chmodels.EventDay.objects.get(dayid=ticket.dayid,eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,)
            if eventday.ticket_required and eventday.arrange:
                    registration.seat_number=arrangeattendee(ticket,hostedevent,registration)
                    registration.day= True
                    registration.dayid= ticket.dayid
                    registration.save()            

    return {'eventtitle':hostedevent.title,'registered':False}

@login_required
def boughtticket(request,eventid=None,hostedeventid=None,ticketid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'children/event_details.html'  
    member = allObject['member']
    transaction_reference=request.POST.copy().get('reference')
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    ticket = chmodels.EventTicket.objects.get(ticketid=ticketid,eventid=eventid,hostedeventid=hostedeventid,)
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
        template_name = 'children/success.html'
        allObject['message'] = 'Congratulations! You have registered for ' + eventtitle
        message = loader.render_to_string(template_name,allObject,request)
        template_name = 'children/attendee_event_manager.html'
        return attendeemanager(request,hostedevent,message)




@login_required
def boughtdayticket(request,eventid=None,hostedeventid=None,ticketid=None,dayid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'children/event_details.html'  
    member = allObject['member']
    transaction_reference=request.POST.copy().get('reference')
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    ticket = chmodels.EventTicket.objects.get(ticketid=ticketid,eventid=eventid,hostedeventid=hostedeventid,)
    eventday = chmodels.EventDay.objects.get(dayid=dayid,eventid=eventid,hostedeventid=hostedeventid,)
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
            template_name = 'children/success.html'
            allObject['message'] = 'Congratulations! You have registered for ' + registered['eventtitle']
            message = loader.render_to_string(template_name,allObject,request)
            template_name = 'children/attendee_event_manager.html'
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
                eventday = chmodels.EventDay.objects.get(eventid=eventid,hostedeventid=hostedeventid,dayid=dayid)
                eventday.arrangements.add(arrangement.instance)
                arrangement.save()
            allObject['hostedevent'] = hostedevent
            updateeventstatus(hostedevent)

            if action == 'next':
                template_name = 'children/create_event_arrangement_modal.html'
                content = loader.render_to_string(template_name,allObject,request)
                event_details_template = 'children/hosted_event_manager.html'
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
                event_details_template = 'children/hosted_event_manager.html'
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
        template_name = 'children/create_event_arrangement_modal.html'
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
    event=chmodels.Event.objects.get(eventid=eventid)
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
                eventday = chmodels.EventDay.objects.get(eventid=eventid,hostedeventid=hostedeventid,dayid=dayid)
                eventday.tickets.add(ticket.instance)
                ticket.save()
            errors= updateeventstatus(hostedevent)
            allObject['hostedevent'] = hostedevent

            if action == 'next':
                template_name = 'children/create_event_ticket_modal.html'
                content = loader.render_to_string(template_name,allObject,request)
                event_details_template = 'children/hosted_event_manager.html'
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
                event_details_template = 'children/hosted_event_manager.html'
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
        template_name = 'children/create_event_ticket_modal.html'
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
    event=chmodels.Event.objects.get(eventid=eventid)
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
        eventday = chmodels.EventDay.objects.create(arrange=arrange,special_offer=specialoffer, ticket_required=ticketing,
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
                template_name = 'children/create_event_day.html'
                content = loader.render_to_string(template_name,allObject,request)
                event_details_template = 'children/hosted_event_manager.html'
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
                    event_details_template = 'children/hosted_event_manager.html'
                    event_details = loader.render_to_string(event_details_template,allObject,request)
                    output_data = { 
                                    'eventdaycreated':True,
                                    'message':'day added',
                                    'content':event_details,
                                    'exit':True
                                    
                                }
                    return JsonResponse(output_data)
    else:
           
        template_name = 'children/create_event_day.html'
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
    event=chmodels.Event.objects.get(eventid=eventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    eventday = chmodels.EventDay.objects.get(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=dayid)
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
        eventday = chmodels.EventDay.objects.filter(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=dayid).update(
        end_date_time=end_date_time_obj, start_date_time=start_date_time_obj, title= str(request.POST.copy().get('title')),arrange=arrange,special_offer=specialoffer, ticket_required=ticketing,)
        eventday = chmodels.EventDay.objects.get(eventid=hostedevent.eventid,hostedeventid=hostedevent.hostedeventid,dayid=dayid)
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
        # event_details_template = 'children/hosted_event_manager.html'
        # event_details = loader.render_to_string(event_details_template,allObject,request)
        # output_data = { 
        #                 'done':True,
        #                 'message':'day edited',
        #                 'content':event_details,                            
        #             }
        # return JsonResponse(output_data)
    else:
           
        template_name = 'children/edit_event_day.html'
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
                    template_name = 'children/success.html'
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
    event=chmodels.Event.objects.get(eventid=eventid,host=member)
    allObject['event']=event
    if request.method == 'POST':
        form = uforms.hostevent(request.POST,request.FILES)
        if form.is_valid():
            # attendance_limit = str(request.POST.copy().get('attendance_limit'))

            specialoffer = str(request.POST.copy().get('offer'))
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
            hostedevent = mmodels.HostedEvent.objects.create(one_day=one_day, one_time_ticketing=ticketing,one_time_arrangement=arrange, eventid=eventid, verification_steps=verification_steps, end_date_time=end_date_time_obj, start_date_time=start_date_time_obj, title=form.cleaned_data['title'],)
            hostedevent.refresh_from_db()
            hostedeventinstance = uforms.hostevent(request.POST,request.FILES,instance=hostedevent)
            hostedeventinstance.save()
            hostedevent.save()
            hostedevent.refresh_from_db()
            if ticketing:
                for eventday in hostedevent.days.all():
                    eventday.ticket_required = True
                    eventday.save()
            if arrange:
                for eventday in hostedevent.days.all():
                    eventday.arrange = True
                    eventday.save() 
            allObject['hostedevent'] = hostedevent
            event.hosted_events.add(hostedevent)
            # if ticketing:
            #     template_name = 'children/create_event_ticket.html'
            #     content = loader.render_to_string(template_name,allObject,request)
            #     event_details_template = 'children/hosted_event_manager.html'
            #     event_details = loader.render_to_string(event_details_template,allObject,request)
            #     output_data = { 
            #                     'done':True,
            #                     'message':'hosted',
            #                     'modal_content':content,
            #                     'content':event_details
                                
            #                 }
            #     return JsonResponse(output_data)
            # elif arrange==True:
            #     template_name = 'children/create_event_arrangement.html'
            #     content = loader.render_to_string(template_name,allObject,request)
            #     event_details_template = 'children/hosted_event_manager.html'
            #     event_details = loader.render_to_string(event_details_template,allObject,request)
            #     output_data = { 
            #                     'done':True,
            #                     'message':'hosted',
            #                     'modal_content':content,
            #                     'content':event_details
                                
            #                 }
            #     return JsonResponse(output_data)
            template_name = 'children/hosted_events.html'
            content = loader.render_to_string(template_name,allObject,request)
            output_data = { 
                            'done':True,
                            'message':'hosted',
                            'modal_content':content,
                            
                        }
            return JsonResponse(output_data) 
        else:
            allObject['url'] = request.get_full_path()
            template_name ='children/host_event.html'
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
        template_name = 'children/host_event.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'header':'Create Event',
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
            event = mmodels.HostedEvent.objects.create(reoccur=reoccur,reoccurance_frequency=frequency, title=form.cleaned_data['title'], host=member)
            hostedevent.refresh_from_db()
            eventinstance = uforms.addevent(request.POST,request.FILES,instance=event)
            eventinstance.save()
            hostedevent.save()
            redirectaction = redirect('manage_event',eventid=hostedevent.eventid)
            hostedevent.refresh_from_db()
            allObject['hostedevent'] = hostedevent
            output_data = { 
                            'eventcreated':True,
                            'message':'created',
                            'url': redirectaction.url,
                            
                        }
            return JsonResponse(output_data) 
        else:
            allObject['url'] = request.get_full_path()
            template_name ='children/create_event.html'
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
        template_name = 'children/create_event.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'modal_content':content,
                'header':'Create Event',
                        }
        # return JsonResponse(output_data)  
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
        ticket_required=ticketing, host=member,attendance_limit=attendance_limit)
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
        #     template_name ='children/create_event.html'
        #     allObject['form'] = form
        #     content = loader.render_to_string(template_name,allObject,request)
        #     output_data = {
        #         'eventadded':False,
        #         'message':'not added',
        #                         'modal_content':content,
        #                     }
        #     return JsonResponse(output_data)  

    else:
        template_name = 'children/edit_event.html'
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
    event = chmodels.Event.objects.get(eventid=eventid,host=member)
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

        template_name = 'children/hosted_event_manager.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = { 
                        'done':True,
                        'message':'edited',
                        'content':content,
                        
                    }
        return JsonResponse(output_data)

    else:
        template_name = 'children/edit_hosted_event.html'
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
    # template_name = 'children/create_event_ticket_modal.html'
    # content = loader.render_to_string(template_name,allObject,request)
    event_details_template = 'children/hosted_event_manager.html'
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
    ticket = chmodels.EventTicket.objects.get(eventid=eventid,ticketid=ticketid,hostedeventid=hostedevent.hostedeventid)
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
        template_name = 'children/edit_event_ticket.html'
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
    arrangement = chmodels.Arrangement.objects.get(eventid=eventid,arrangementid=arrangementid,hostedeventid=hostedeventid)
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
        template_name = 'children/edit_event_arrangement.html'
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
    ticket = chmodels.EventTicket.objects.get(eventid=eventid,ticketid=ticketid,hostedeventid=hostedeventid)
    hostedevent = mmodels.HostedEvent.objects.get(eventid=eventid,hostedeventid=hostedeventid)
    # event = mmodels.HostedEvent.objects.get(eventid=eventid,host=member)
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
    arrangement = chmodels.Arrangement.objects.get(eventid=eventid,arrangementid=arrangementid,hostedeventid=hostedeventid)
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
    template_name = 'children/profile.html'
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
        template_name = 'children/dashboard_content.html'
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
                reqcontent = chmodels.Article.objects.get(contentid=cid)
            elif str(content).lower() == 'announcement':
                reqcontent = chmodels.Announcement.objects.get(contentid=cid)
            template_name = 'children/information_desk_content.html'
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
        template_name = 'children/events.html'
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
        announcements =  list(chmodels.Announcement.objects.all())
        announcements.sort(key=lambda x: x.date_time_added,reverse=True)
        allObject['announcements'] =announcements
        template_name = 'children/announcements.html'
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
        announcement = chmodels.Announcement.objects.get(contentid=announcementid)
        allObject['announcement'] = announcement
        template_name = 'children/announcement_details.html'
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
        member.mobile1 = phone
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
        template_name = 'children/success.html'
        allObject['message'] = 'Your profile updated'
        successcontent = loader.render_to_string(template_name,allObject,request)
        template_name = 'children/dashboard_content.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'profile_updated':profile_updated,
             'modal_content':content,
             'successcontent':successcontent,
             'header':'Due balance: ' + 'N2000'
                        }
        message = render_to_string('children/update_profile_email.html', {
               'message':mail_body,
               'user':user
            })
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ] 
        # send_mail( subject, message, email_from, recipient_list ) 
        return JsonResponse(output_data)    

    else:
        member =allObject['member']   
        template_name = 'children/update_profile.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'modal_content':content,
                            'header':'Update Profile'
                        }
        return JsonResponse(output_data)    


def videos(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    videos = list(chmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    allObject['videos'] =videos
    template_name = 'children/videos.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'modal_content':content,
                        }
    return JsonResponse(output_data)

