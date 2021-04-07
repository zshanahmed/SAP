"""
Url mappings with appropriate functions to handle them
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'sap'
urlpatterns = [
    path('', auth_views.LoginView.as_view(
        template_name='sap/login.html'), name='home'),

    path('logout/', views.logout_request, name='logout'),

    url(r'login_success/$', views.login_success,
        name='login_success'),

    url(r'^password/$', login_required(views.ChangeAdminPassword.as_view()),
        name='change_password'),
    url(r'^update_profile/$', login_required(views.EditAdminProfile.as_view()),
        name='sap-admin_profile'),
    url(r'^update_ally_profile/$', login_required(views.EditAllyProfile.as_view()),
        name='sap-ally_profile'),

    url(r'^dashboard/$',
        login_required(views.AlliesListView.as_view()),
        name='sap-dashboard'),

    url(r'^ally-dashboard/$',
        login_required(views.MentorsListView.as_view()),
        name='ally-dashboard'),

    url(r'^calendar/$',
        login_required(views.CalendarView.as_view()),
        name='ally-calendar'),

    url('analytics/',
        login_required(views.AnalyticsView.as_view()),
        name='sap-analytics'),

    url('resources/',
        login_required(views.ResourcesView.as_view()),
        name='resources'),

    url(r'password-forgot/$', views.ForgotPasswordView.as_view(),
        name='password-forgot'),

    url(r'password-forgot-done/$', views.ForgotPasswordDoneView.as_view(),
        name='password-forgot-done'),

    # path(r'^password-forgot-confirm/(<slug:uidb64>/<slug:token>/$', auth_views.PasswordResetConfirmView.as_view(),
    #      name='password-forgot-confirm'),

    url(r'password-forgot-confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)$', views.ForgotPasswordConfirmView.as_view(),
        name='password-forgot-confirm'),

    url(r'^allies/$', login_required(views.ViewAllyProfileFromAdminDashboard.as_view()),
        name='admin_view_ally'),

    url(r'^edit_allies/(?P<username>[\w-]+)/$', login_required(views.EditAllyProfile.as_view()),
        name='admin_edit_ally'),
    url(r'^edit_allies/$', login_required(views.EditAllyProfile.as_view()),
        name='admin_edit_ally'),

    url(r'^delete/$', login_required(views.DeleteAllyProfileFromAdminDashboard.as_view()),
        name='admin_delete_ally'),

    url('create_iba_admin/',
        login_required(views.CreateAdminView.as_view()),
        name='create_iba_admin'),

    url('create_event/',
        login_required(views.CreateEventView.as_view()),
        name='create_event'),

    url('about/',
        login_required(views.AboutPageView.as_view()),
        name='sap-about'),

    url('sign-up/', views.SignUpView.as_view(),
        name='sign-up'),

    url(r'sign-up-done/$', views.SignUpDoneView.as_view(),
        name='sign-up-done'),

    url(r'sign-up-confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)$', views.SignUpConfirmView.as_view(),
        name='sign-up-confirm'),

    url(r'^download_allies/$', login_required(views.DownloadAllies.allies_download), name='download_allies'),

    url(r'^upload_allies/$', login_required(views.UploadAllies.upload_allies), name='upload_allies'),
]
