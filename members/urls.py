from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, get_object_or_404
from django.views.static import serve
from members import views as mviews
from general import views as gviews


urlpatterns = [
     path('dashboard/home', mviews.home,name='dashboard_home'),
     path('', mviews.home,name='home'),

     path('dashboard/records', mviews.records,name='dashboard_records'),
     path('dashboard/record/<int:pk>', mviews.record,name='dashboard_record'),
     path('dashboard/incidence/<int:pk>', mviews.incidence,name='dashboard_incidence'),
     path('member/dashboard', mviews.dashboard,name='member_dashboard'),
     path('member/record_attendance', mviews.record_attendance,name='record_attendance'),
     path('member/record_incidence', mviews.record_incidence,name='record_incidence'),
            path('member/events', mviews.eventtab,name='member_event_tab'),
          path('member/home', mviews.hometab,name='member_home_tab'),
     path('member/dashboardcontent', mviews.dashboardcontent,name='member_dashboard_content'),
          path('member/eventregistration/<str:eventid>/<str:hostedeventid>', mviews.eventregistration,name='member_event_registration'),
                  path('member/information_desk_content/<str:content>/<str:cid>', mviews.informationdeskcontent,name='member_information_desk_content'),
      path('member/member/confirmemailpage', mviews.confirmemailpage, name='member_confirm_email_page'),
      path('member/search', mviews.membersearch, name='member_search'),

          path('member/verifyevent', mviews.verifyevent,name='member_verify_event'),
          path('member/profile', mviews.myprofile,name='member_profile'),
          path('member/announcements', mviews.announcements,name='member_announcements'),
          path('member/announcement/<str:announcementid>', mviews.announcementdetails,name='member_announcement_details'),
          path('member/videos', mviews.videos,name='member_videos'),
            path('member/myevents', mviews.myevents,name='member_my_events'),
          path('member/hostevent/<str:eventid>', mviews.hostevent,name='member_host_event'),

          path('member/createevent', mviews.createevent,name='member_create_event'),
          path('member/editevent/<str:eventid>/<str:hostedeventid>', mviews.edithostedevent,name='member_edit_hosted_event'),
          path('member/editevent/<str:eventid>', mviews.editevent,name='member_edit_event'),
          path('member/editticket/<str:eventid>/<str:hostedeventid>/<str:ticketid>', mviews.editticket,name='member_edit_hosted_event_ticket'),
          path('member/editarrangement/<str:eventid>/<str:hostedeventid>/<str:arrangementid>', mviews.editarrangement,name='member_edit_hosted_event_arrangement'),
          path('member/deletearrangement/<str:eventid>/<str:hostedeventid>/<str:arrangementid>', mviews.deletearrangement,name='member_delete_hosted_event_arrangement'),
          path('member/deleteticket/<str:eventid>/<str:ticketid>/<str:hostedeventid>', mviews.deleteticket,name='member_delete_hosted_event_ticket'),
          path('member/createeventticket/<str:eventid>/<str:hostedeventid>/<str:dayid>/<str:action>', mviews.createeventticket,name='member_create_hosted_event_ticket'),
          path('member/createeventday/<str:eventid>/<str:hostedeventid>/<str:scope>/<str:action>', mviews.createeventday,name='member_create_hosted_event_day'),
          path('member/deleteeventday/<str:eventid>/<str:hostedeventid>/<str:dayid>', mviews.deleteeventday,name='member_delete_hosted_event_day'),          
          path('member/editeventday/<str:eventid>/<str:hostedeventid>/<str:dayid>', mviews.editeventday,name='member_edit_hosted_event_day'),
          path('member/eventdaydetails/<str:eventid>/<str:hostedeventid>/<str:dayid>', mviews.eventdaydetails,name='member_event_day_details'),
          path('member/eventdayregistration/<str:eventid>/<str:hostedeventid>/<str:dayid>', mviews.eventdayregistration,name='member_event_day_registration'),
          path('member/createeventarrangement/<str:eventid>/<str:hostedeventid>/<str:dayid>/<str:action>', mviews.createeventarrangement,name='member_create_hosted_event_arrangement'),
          path('member/manageevent/<str:eventid>/<str:hostedeventid>', mviews.manageevent,name='member_manage_event'),
          path('member/publishevent/<str:eventid>/<str:hostedeventid>', mviews.publishevent,name='member_publish_hosted_event'),

          path('member/unpublishevent/<str:eventid>/<str:hostedeventid>', mviews.unpublishevent,name='member_unpublish_hosted_event'),
          path('member/viewevent/<str:eventid>', mviews.viewevent,name='member_view_event'),
          path('member/member/identity', mviews.memberidentity,name='member_identity'),
          path('member/event/qrcode/<str:eventid>/<str:hostedeventid>', mviews.eventqrcode,name='member_event_qrcode'),
          path('member/event/attendee/qrcode/<str:eventid>', mviews.attendeeqrcode,name='member_attendee_qrcode'),
          path('member/eventdetails/<str:eventid>/<str:hostedeventid>', mviews.eventdetails,name='member_event_details'),
          path('member/event_qrcode_attendance/<str:eventid>/<str:hostedeventid>', mviews.attendeeqrcverification,name='member_event_qrcode_attendance'),
          path('member/boughtdayticket/<str:eventid>/<str:hostedeventid>/<str:ticketid>/<str:dayid>', mviews.boughtdayticket,name='member_bought_day_ticket'),

          path('member/boughtticket/<str:eventid>/<str:hostedeventid>/<str:ticketid>/<str:dayid>', mviews.boughtticket,name='member_bought_ticket'),
          path('member/buyticket/<str:eventid>/<str:hostedeventid>', mviews.buyticket,name='member_buy_ticket'),
          path('member/host_qrcode_verification/<str:eventid>/<str:hostedeventid>', mviews.hostqrcverification,name='member_host_qrcode_verification'),

     path('member/events', mviews.events,name='member_events'),

       path('member/update_profile', mviews.updateprofile,name='member_update_profile'),

    url('activate-account', gviews.activate, name='activate_account'),
    url('createwallet', gviews.createaccounts, name='create_accounts'),
    url('resendactivationcode', gviews.resendactivationcode, name='resend_activation_code'),
    # url('unsuspend', gviews.unsuspend, name='unsuspend'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
