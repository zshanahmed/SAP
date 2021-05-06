"""
Url mappings with appropriate functions to handle them
"""
import notifications.urls
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

import sap.views_v2
import sap.views_v3
from . import views

app_name = 'sap'
urlpatterns = [
    path('',
         auth_views.LoginView.as_view(template_name='sap/login.html',
                                      redirect_authenticated_user=True),
         name='home'),

    path('logout/', views.logout_request,
         name='logout'),

    url(r'login_success/$', views.login_success,
        name='login_success'),

    url(r'^password/$', login_required(views.ChangeAdminPassword.as_view()),
        name='change_password'),
    url(r'^update_profile/$', login_required(views.EditAdminProfile.as_view()),
        name='sap-admin_profile'),

    url(r'^dashboard/$',
        login_required(views.AlliesListView.as_view()),
        name='sap-dashboard'),

    url(r'^ally-dashboard/$',
        login_required(views.MentorsListView.as_view()),
        name='ally-dashboard'),

    url(r'^calendar/$',
        login_required(views.CalendarView.as_view()),
        name='calendar'),

    url(r'^delete_event/$', login_required(sap.views_v3.DeleteEventView.as_view()),
        name='admin_delete_event'),

    url(r'^edit_event/$', login_required(sap.views_v3.EditEventView.as_view()), name='edit_event'),

    url('analytics/',
        login_required(views.AnalyticsView.as_view()),
        name='sap-analytics'),

    url('resources/',
        login_required(views.ResourcesView.as_view()),
        name='resources'),

    url(r'password-forgot/$', sap.views_v2.ForgotPasswordView.as_view(),
        name='password-forgot'),

    # url(r'password-forgot-done/$', sap.views_v2.ForgotPasswordDoneView.as_view(),
    #     name='password-forgot-done'),

    url(r'password-forgot-confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)$', sap.views_v2.ForgotPasswordConfirmView.as_view(),
        name='password-forgot-confirm'),

    url(r'^allies/(?P<ally_username>[\s\w-]+)/$', login_required(views.ViewAllyProfileFromAdminDashboard.as_view()),
        name='admin_view_ally'),

    url(r'^edit_allies/(?P<username>[\s\w-]+)/$',
        login_required(sap.views_v3.EditAllyProfile.as_view()),
        name='admin_edit_ally'),

    url(r'^view-ally-event-info/(?P<ally_username>[\s\w-]+)/$', login_required(sap.views_v3.AllyEventInformation.as_view()),
        name='view_ally_event_information'),

    url(r'^delete/$', login_required(views.DeleteAllyProfileFromAdminDashboard.as_view()),
        name='admin_delete_ally'),

    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),

    url('create_iba_admin/',
        login_required(views.CreateAdminView.as_view()),
        name='create_iba_admin'),

    url('create_event/',
        login_required(views.CreateEventView.as_view()),
        name='create_event'),

    url(r'^signup_event/$',
        login_required(sap.views_v2.SignUpEventView.as_view()),
        name='signup_event'),

    url(r'^signup_event/(?P<context>[\s\w-]+)/$',
        login_required(sap.views_v2.SignUpEventView.as_view()),
        name='signup_event'),

    url(r'^deregister_event/$',
        login_required(sap.views_v3.DeregisterEventView.as_view()),
        name='deregister_event'),

    url(r'^deregister_event/(?P<context>[\s\w-]+)/$',
        login_required(sap.views_v3.DeregisterEventView.as_view()),
        name='deregister_event'),

    url(r'^announcements/$',
        login_required(views.Announcements.as_view()),
        name='announcements'),

    url('about/',
        login_required(views.AboutPageView.as_view()),
        name='sap-about'),

    url('sign-up/', sap.views_v2.SignUpView.as_view(),
        name='sign-up'),

    # url(r'sign-up-done/$', sap.views_v2.SignUpDoneView.as_view(),
    #     name='sign-up-done'),

    url(r'sign-up-confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)$', sap.views_v2.SignUpConfirmView.as_view(),
        name='sign-up-confirm'),

    url(r'^download_allies/$', login_required(sap.views_v2.DownloadAllies.allies_download), name='download_allies'),
    url(r'^create_announcements/$',
        login_required(views.CreateAnnouncement.create_announcement), name='create_announcement'),

    url(r'^notification_center/$',
        login_required(sap.views_v3.SapNotifications.as_view()), name='notification_center'),

    url(r'^upload_allies/$', login_required(sap.views_v2.UploadAllies.upload_allies), name='upload_allies'),

    url(r'^dismiss_notification/(?P<notification_id>[\w-]+)/$',
        login_required(sap.views_v3.SapNotifications.dismiss_notification),
        name='dismiss_notification'),

    url(r'notify_mentor/(?P<mentor_requested_username>[\w\s-]+)$',
        login_required(sap.views_v3.MentorshipView.make_mentor_notification), name='notify_mentor'),

    url(r'notify_mentee/(?P<mentee_requested_username>[\w\s-]+)/$',
        login_required(sap.views_v3.MentorshipView.make_mentee_notification), name='notify_mentee'),

    url(r'add_mentor/(?P<mentor_username>[\w\s-]+)$',
        login_required(sap.views_v3.MentorshipView.make_mentor_mentee), name='add_mentor'),


    url(r'add_mentee/(?P<mentee_username>[\w\s-]+)$',
        login_required(sap.views_v3.MentorshipView.make_mentee_mentor), name='add_mentee')
]
