from django.contrib.auth.hashers import is_password_usable, make_password
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from geoip2.records import Location
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
from general import models as gmodels
from members import views as pviews
from members import models as mmodels
from ipware import get_client_ip
import geoip2.database
import requests
import json


allObject = {}
import socket

def logrequest(request,memberid=''):
    hostname = socket.gethostname()
    ip_1 = socket.gethostbyname(hostname)
    ip_2, is_routable = get_client_ip(request)
    if ip_2 is None:
        pass
    else:
        # We got the client's IP address
        if is_routable:
            pass
            # The client's IP address is publicly routable on the Internet
        else:
            pass
            # The client's IP address is private
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip_3 = s.getsockname()[0]
    except Exception:
        ip_3 = '127.0.0.1'
    finally:
        s.close()
    try:
        response = requests.get('https://api.ipify.org').text
    # result  = response.json()
        location = response
    except Exception:
        location=''
    requestlog = gmodels.RequestLog.objects.create(memberid=memberid, url = request.path,ip_1=ip_1,ip_2=ip_2,ip_3=ip_3,host_name=hostname,location=location)
    return True


def inherit(request, *args, **kwargs):
    allObject ={}
    try:
        settings = list(gmodels.General.objects.all())[0]
    except IndexError:
        settings = []
    allObject['settings'] = settings
    allObject['server_timestamp'] = round(datetime.datetime.now().timestamp())
    # logrequest(request)

    return allObject



def gallery(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/gallery.html'
    page = request.GET.get('page', 1)

    allObject['page'] = page
    content = loader.render_to_string(template_name,allObject,request)
    template_name = 'general/gallery.html'
    return render(request,template_name,allObject)



def gallerycontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/gallery_content.html'
    gallery = list(gmodels.Gallery.objects.all())
    gallery.sort(key=lambda x: x.date_time_added,reverse=True)
    page = request.GET.get('page')
    paginator = Paginator(gallery, 8)
    try:
        gallery = paginator.get_page(page)
    except PageNotAnInteger:
        gallery = paginator.get_page(1)
    except EmptyPage:
        gallery = paginator.get_page(paginator.num_pages)
    allObject['gallery'] = gallery

    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)

def momentoftruth(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/moment_of_truth.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def momentoftruthcontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/moment_of_truth_content.html'
    tvs = list(gmodels.TvStation.objects.all())
    allObject['tvs'] = tvs
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def upcomingevents(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/upcoming_events.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def upcomingeventscontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/upcoming_events_content.html'
    upcomingevents = list(gmodels.Event.objects.all())
    upcomingevents =  list(gmodels.Event.objects.filter(start_date_time__gt = datetime.datetime.now()))
    allObject['upcomingevents'] =upcomingevents    
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)





def pastevents(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/past_events.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def pasteventscontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/past_events_content.html'
    pastevents =  list(gmodels.Event.objects.filter(end_date_time__lt = datetime.datetime.now(),start_date_time__lt=datetime.datetime.now()))
    pastevents.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['pastevents'] =pastevents
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)





def videos(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/videos.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def videoscontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/videos_content.html'
    videos = list(gmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    allObject['videos'] =videos
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def home(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'general/home.html'
    return render(request,template_name,allObject)

def slideshow(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    slideshows = gmodels.SlideShow.objects.all()
    allObject['slideshows'] = slideshows
    template_name = 'general/slideshow.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def galleryhome(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    gallery = list(gmodels.Gallery.objects.all())
    gallery.sort(key=lambda x: x.date_time_added,reverse=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(gallery, 7)
    try:
        gallery = paginator.page(page)
    except PageNotAnInteger:
        gallery = paginator.page(1)
    except EmptyPage:
        gallery = paginator.page(paginator.num_pages)
    allObject['gallery'] = gallery
    template_name = 'general/home_gallery.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)


def sendmessage(request, *args, **kwargs):
    allObject= inherit(request, *args, **kwargs)
    if request.method == 'POST':
        newmessage = str(request.POST.copy().get('message'))
        fullname = str(request.POST.copy().get('name'))
        phonenumber = str(request.POST.copy().get('phonenumber'))
        email = str(request.POST.copy().get('email'))
        message = gmodels.ContactMessage.objects.create(name=fullname,email=email,number=phonenumber,message=newmessage)
        message.refresh_from_db()
        subject = 'New Message'
        current_site = Site.objects.get_current()


        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [message.email, ] 
        message = render_to_string('general/new_message.html', {
                'message': message,
            })
        send_mail( subject, message, email_from, recipient_list ) 
        template_name = 'general/success.html'
        allObject['message'] = 'Your Message was sent successfully'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'sent':True,
            'content':content,
                            }
        return JsonResponse(output_data)


def kingdomstrategieshome(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    videos = list(gmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    # allObject['videos'] =videos
    articles = list(gmodels.Article.objects.all())
    articles.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestarticle'] = articles[0]
    articles.remove(articles[0])
    allObject['articles'] =articles
    template_name = 'general/home_kingdom_strategies.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)


def events(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    upcomingevents =  list(gmodels.Event.objects.filter(start_date_time__gt = datetime.datetime.now()))
    upcomingevents.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['upcomingevents'] =upcomingevents
    pastevents =  list(gmodels.Event.objects.filter(end_date_time__lt = datetime.datetime.now(),start_date_time__lt=datetime.datetime.now()))
    pastevents.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['pastevents'] =pastevents
    template_name = 'general/events.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def pastorsdesk(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    pastorsdesk = list(gmodels.PastorsDesk.objects.all())[0]
    allObject['pastorsdesk'] = pastorsdesk

    template_name = 'general/pastors_desk.html'
    return render(request,template_name,allObject)


def contactus(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)

    template_name = 'general/contact.html'
    return render(request,template_name,allObject)


def kingdomstrategies(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    allObject['pastorsdesk'] = pastorsdesk
    videos = list(gmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    videos.remove(videos[0])
    allObject['videos'] =videos
    articles = list(gmodels.Article.objects.all())
    articles.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['articles'] =articles
    template_name = 'general/kingdom_strategies.html'
    return render(request,template_name,allObject)



@login_required
def unsuspend(request, *args, **kwargs):
    user = User.objects.get(email=request.user.email)
    try:
        member = mmodels.Member.objects.get(user=user)
        member.briefly_suspended = False
        member.suspension_count =0
        member.save()
        output_data = {
            'member':True,
            'unsuspended':True,
                            }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        member = mmodels.member.objects.get(user=user)
        member.briefly_suspended = False
        member.suspension_count = 0
        member.save()
        output_data = {
            'member':True,
            'unsuspended':True,
                            }
        return JsonResponse(output_data)



# @login_required
# def home(request, *args, **kwargs):
#     user = User.objects.get(email=request.user.email)
#     try:
#         member = mmodels.member.objects.get(user=user)
#         member = True
#         return cviews.home(request, *args, **kwargs)
#     except ObjectDoesNotExist:
#         member = mmodels.member.objects.get(user=user)
#         member=True 
#         return cviews.home(request, *args, **kwargs)    

def loginuser(request, *args, **kwargs):
    # if request.user.is_authenticated:
    #     return redirect('account_login')
    auth.logout(request)
    if request.method == 'POST':
        username = request.POST.copy().get('username').lower()
        raw_password = request.POST.copy().get('password')
        try:
            user = User.objects.get(username=username,is_active=True)
            user = authenticate(username=username, password=raw_password)
        except ObjectDoesNotExist:
            try:
                user = User.objects.get(email=username,is_active=True)
                user = authenticate(username=user.username, password=raw_password)
            except ObjectDoesNotExist:
                output_data = {
                    'invalid':True,
                    'modal_notification':'Invalid login details'
                }
                return JsonResponse(output_data)
        if user is None:
            output_data = {
                'invalid':True,
                'modal_notification':'Invalid login details'
            }
            return JsonResponse(output_data) 
            
        else:
            login(request, user)   
        allObject = inherit(request)
        template_name = 'members/dashboard.html'
        content = loader.render_to_string(template_name,allObject,request)
        if request.POST.copy().get('next'):
                redirectinstance= redirect(request.POST.copy().get('next')).url
        else:
                redirectinstance= '/'
   
        output_data = {
                            'logged_in':True,
                            'url':redirectinstance
                        }
        return JsonResponse(output_data)



    else:
        form = allauthforms.LoginForm()
        # allObject['form'] = form
        # if request.GET.get('next'):
        #     allObject['next_page']=request.GET.get('next')
        #     allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/member_lookup.html'
        return render(request,template_name,allObject)
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                        }
        return JsonResponse(output_data)



def memberlookup(request, *args, **kwargs):
    auth.logout(request)
    # if request.user.is_authenticated:
    #     logout(request)
    #     return redirect('account_login')
    allObject = inherit(request, *args, **kwargs)

    if request.method == 'POST':
    #form =allauthforms.LoginForm(request.POST)
    #if form.is_valid():
        uniqueidentifier = request.POST.copy().get('identifier').lower()
        try:
            profile = mmodels.ApprovedUser.objects.get(phone_number=uniqueidentifier)
        except ObjectDoesNotExist:
            try:
                profile = mmodels.ApprovedUser.objects.get(email=uniqueidentifier)
            except ObjectDoesNotExist:
                output_data = {
                    'invalid':True,
                    'error':'Record not found. Try another Phone number or Email'
                }
                return JsonResponse(output_data)
        # try:
        #     member = profile
        # except ObjectDoesNotExist:
        #     allObject['identifier']=uniqueidentifier

        #     allObject['profile']=profile
        #     template_name = 'allauth/account/create_password.html'
        #     content = loader.render_to_string(template_name,allObject,request)
        #     output_data = {
        #                 'form_content':content,
        #             }
        #     return JsonResponse(output_data)   
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        allObject['identifier']=profile.email

        allObject['profile']=profile
        template_name = 'allauth/account/enter_password.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                    'form_content':content,
                }
        return JsonResponse(output_data)
        login(request, user)   
        member = True
        allObject = inherit(request)
        member = mmodels.Member.objects.get(user=user,dependant=False)
        member = True
        template_name = 'members/dashboard.html'
        content = loader.render_to_string(template_name,allObject,request)
        if request.POST.copy().get('next'):
                redirectinstance= redirect(request.POST.copy().get('next'))
        output_data = {
                            'logged_in':True,
                            'url':redirectinstance.url
                        }
        return JsonResponse(output_data)



    else:
        form = allauthforms.LoginForm()
        allObject['form'] = form
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/member_lookup.html'
        return render(request,template_name,allObject)
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                        }
        return JsonResponse(output_data)



def membersignup(request, *args, **kwargs):
    if request.method == 'POST':
        uniqueidentifier = request.POST.copy().get('identifier').lower()
        password = request.POST.copy().get('password')
        try:
            profile = mmodels.LraMembersBiodata.objects.get(mobile1=uniqueidentifier)
        except ObjectDoesNotExist:
            try:
                profile = mmodels.LraMembersBiodata.objects.get(email=uniqueidentifier)
            except ObjectDoesNotExist:
                pass
        formerrors = []
        try:
            user= User.objects.get(username=uniqueidentifier)
            formerrors.append("<li class='text-sm uk-text-bold'>Username/Phone number already taken</li>")

        except ObjectDoesNotExist:
            try:
                user= User.objects.get(email=uniqueidentifier)
                formerrors.append("<li class='text-sm uk-text-bold'>Email already taken</li>")

            except ObjectDoesNotExist:
                pass
        if formerrors:
            erroroutput ="<ul class='text-danger p-0'>"
            errorlist = ''
            for error in formerrors:
                errorlist += '<li>' +str(error)+'</li>'
            erroroutput += errorlist + '</ul>'
            output_data = { 
                            'invalid':True,
                            'modal_notification':'<b>Ooops... Something is wrong!</b>' + erroroutput,
                            
                        }
            return JsonResponse(output_data)
        harshed_password = make_password(password)
        user = User.objects.create(password=harshed_password, username=profile.mobile1 or profile.email, 
        first_name =profile.firstname,last_name= profile.surname,
        email= profile.email)
        user.refresh_from_db()
        user.is_active = True
        user.save()
        # form.user_id = user_id
        chars = '0123456789' 
        token = ''
        for num in range(0,len(chars)):
            token = token +chars[round((random()-0.5)*len(chars))]
        token = token[0:6]
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
            firstletter= user.first_name[0].upper()
            lastletter =user.last_name[0].upper()
            temporary_userid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
            userid= []
            for char in temporary_userid:
                userid.insert(round(random()*5),char)
            userid = ''.join(userid)
            userid = 'CGCC'+userid
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
            firstletter= user.first_name[0].upper()
            lastletter =user.last_name[0].upper()
            temporary_familyid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
            familyid= []
            for char in temporary_familyid:
                familyid.insert(round(random()*5),char)
            familyid = ''.join(familyid)
            familyid = 'CGCC'+familyid
            try:                
                mmodels.Member.objects.get(memberid=userid)

            except ObjectDoesNotExist:
                mmodels.Member.objects.create(user=user,bio_data=profile,familyid=familyid, memberid=userid,last_token=token)
                exist = False
        # subject = 'welcome to CGCC'
        # current_site = Site.objects.get_current()

        # message = render_to_string('allauth/account/email_confirm.html', {
        #         'token': token,
        #     })
        # email_from = settings.EMAIL_HOST_USER 
        # recipient_list = [user.email, ]
        # try:
        #     send_mail( subject, message, email_from, recipient_list )
        # except socket.gaierror:
        #     pass
        user.is_active = True
        user.save()
        login(request, user)
        allObject = inherit(request)
        member = mmodels.Member.objects.get(user=user)
        member = True
        template_name = 'members/dashboard.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'logged_in':True,
                        }
        return JsonResponse(output_data)


def newmembersignup(request, *args, **kwargs):
    if request.method == 'POST':
        form = gforms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email=form.cleaned_data['email']
            user.is_active = False
            user.save()
            # form.user_id = user_id
            chars = '0123456789' 
            token = ''
            for num in range(0,len(chars)):
                token = token +chars[round((random()-0.5)*len(chars))]
            token = token[0:6]
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
                firstletter= user.first_name[0].upper()
                lastletter =user.last_name[0].upper()
                temporary_userid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
                userid= []
                for char in temporary_userid:
                    userid.insert(round(random()*5),char)
                userid = ''.join(userid)
                userid = 'CGCC'+userid
                try:                
                    mmodels.Member.objects.get(memberid=userid)
                except ObjectDoesNotExist:
                    mmodels.Member.objects.create(user=user,memberid=userid,last_token=token,phone_number = request.POST.copy().get('phone_number'))
                    exist = False
            subject = 'welcome to Dominion Members'
            current_site = Site.objects.get_current()

            message = render_to_string('allauth/account/email_confirm.html', {
                    'token': token,
                })
            email_from = settings.EMAIL_HOST_USER 
            recipient_list = [user.email, ]
            try:
                send_mail( subject, message, email_from, recipient_list )
            except socket.gaierror:
                pass
            user.is_active = True
            user.save()
            login(request, user)
            allObject = inherit(request)
            member = mmodels.Member.objects.get(user=user)
            member = True
            template_name = 'members/dashboard.html'
            content = loader.render_to_string(template_name,allObject,request)
            output_data = {
                                'logged_in':True,
                            }
            return JsonResponse(output_data)
        else:
            formerrors = []
            # try:
            #     user = User.objects.get(username=str(request.POST.copy().get('username')))
            #     formerrors.append('<li>username already taken</li>')
            # except ObjectDoesNotExist:
            #     pass
            try:
                user = User.objects.get(email=str(request.POST.copy().get('email')))
                formerrors.append('<li>Email already taken</li>')
            except ObjectDoesNotExist:
                pass
            for error in form.errors:
                # formerrors.append(error)
                formerrors.append(form.errors[error])
            erroroutput ="<ul class='text-danger p-0'>"
            errorlist = ''
            for error in formerrors:
                errorlist += '<li>' +str(error)+'</li>'
            erroroutput += errorlist + '</ul>'
            output_data = { 
                            'invalid':True,
                            'modal_notification':'<b>Ooops... Something is wrong!</b>' + erroroutput,
                            
                        }
            return JsonResponse(output_data)
            output_data = {
                'invalid':True,
                'modal_notification':formerrors
            }
            return JsonResponse(output_data)


    else:
        form = gforms.SignUpForm()
        allObject = inherit(request, *args, **kwargs)
        allObject['form'] = form
        return render(request, 'allauth/account/signup.html', allObject)



def logoutuser(request, *args, **kwargs):
    auth.logout(request)
    form = allauthforms.LoginForm()
    allObject = inherit(request, *args, **kwargs)
    allObject['form'] = form
    template_name = 'allauth/account/login.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'loggedout':True,
                    }
    return JsonResponse(output_data)


@login_required

def account_activation_sent(request,*args, **kwargs):
    template_name = 'allauth/account/verification_sent.html'
    return render(request,template_name)



@login_required
def createaccounts(request,*args, **kwargs):
    user = User.objects.get(email=request.user.email)
    try:
        member = mmodels.member.objects.get(user=user)
        try:
            gmodels.SavingsAccount.objects.get(member=member)

        except ObjectDoesNotExist:
            gmodels.SavingsAccount.objects.create(member=member,number=str(round(random()*1234567890999))[0:10])
        try:
            gmodels.DebitAccount.objects.get(member=member)

        except ObjectDoesNotExist:
            gmodels.DebitAccount.objects.create(member=member,number=str(round(random()*1234567890999))[0:10])
        member.accounts_created = True
        member.save()
        output_data = {
                    'accounts_created':True,
                }
        return JsonResponse(output_data)  
    except ObjectDoesNotExist:
        member = mmodels.member.objects.get(user=user)
        try:
            gmodels.Wallet.objects.get(userid=member.userid)
            output_data = {
                        'wallet_created':True,
                    }
            return JsonResponse(output_data) 
        except ObjectDoesNotExist:
            gmodels.Wallet.objects.create(userid=member.userid,number=str(round(random()*1234567890999))[0:10])
            output_data = {
                        'wallet_created':True,
                    }
            return JsonResponse(output_data)        


@login_required
def activate(request,*args, **kwargs):
    if request.method=='POST':
        user = User.objects.get(email=request.user.email)
        activation_code = request.POST.copy().get('activation_code')
        try:
                member = mmodels.Member.objects.get(user=user,dependant=False)
        except ObjectDoesNotExist:
                member = mmodels.Member.objects.get(user=user,dependant=False)
        if member.last_token == activation_code:
            member.email_confirmed = True
            member.last_token=''
            member.save()
            output_data = {
                        'activated':True,
                    }
            return JsonResponse(output_data)
        else:
            output_data = {
                        'invalid_code':True,
                    }
            return JsonResponse(output_data)





@login_required
def resendactivationcode(request,*args, **kwargs):
    chars = '0123456789'
    token = ''
    for num in range(0,len(chars)):
        token = token +chars[round((random()-0.5)*len(chars))]
    token = token[0:6] 
    try:
        member = mmodels.Member.objects.get(user=User.objects.get(email=request.user.email))
        member.last_token=token
        member.save()
        subject = 'DPG - Activation Code'
        user = request.user
        current_site = Site.objects.get_current()
        current_site = Site.objects.get_current()

        message = render_to_string('allauth/account/email_confirm.html', {
                'token':member.last_token,
                'user':member.user
            })
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [user.email, ] 
        try:
            send_mail( subject, message, email_from, recipient_list ) 
        except socket.gaierror:
            pass
        output_data = {
                        'email_sent':True,
                        'modal_notification':'your activation code has been resent to '+user.email,
                            }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        member = mmodels.member.objects.get(user=User.objects.get(email=request.user.email))
        member.last_token = token
        member.save()
        subject = 'Sickle - Activation Code'
        user = request.user
        current_site = Site.objects.get_current()
        subject = 'welcome to Sickle Saving App'
        current_site = Site.objects.get_current()

        message = render_to_string('allauth/account/email_confirm.html', {
                'token':member.last_token,
            })
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [user.email, ] 
        send_mail( subject, message, email_from, recipient_list )
        output_data = {
                        'email_sent':True,
                                'message':'your activation code has been resent to '+user.email,
                            }
        return JsonResponse(output_data)