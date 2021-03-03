from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

app_name = 'sap'
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='sap/login.html'), name='home'),

    path('logout/', views.logout_request, name='logout'),

    url(r'login_success/$', views.login_success, name='login_success'),

    url(r'^password/$', login_required(views.ChangeAdminPassword.as_view()),
        name='change_password'),
    url(r'^update_profile/$', login_required(views.EditAdminProfile.as_view()),
        name='sap-admin_profile'),

    url(r'^dashboard/$',
        login_required(views.AlliesListView.as_view(), login_url='home'),
        name='sap-dashboard'),

    url('analytics/',
        login_required(views.AnalyticsView.as_view(), login_url='home'),
        name='sap-analytics'),

    url(r'forgot-password/$', views.ForgotPasswordView.as_view(), name='forgot_password'),

    url('create_iba_admin/',
        login_required(views.CreateAdminView.as_view(), login_url='home'),
        name='create_iba_admin'),

    url('about/',
        login_required(views.AboutPageView.as_view(), login_url='about'),
        name='sap-about'),
]
