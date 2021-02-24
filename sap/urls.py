from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from . import views
from .views import MessageBoardView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='sap/login.html'), name='home'),
    path('logout/', auth_views.LogoutView.as_view(template_name='sap/logout.html'), name='logout'),


    url(r'^dashboard/$',
        login_required(views.AlliesListView.as_view(), login_url='home'),
        name='sap-dashboard'),
    url('analytics/',
        login_required(views.AnalyticsView.as_view(), login_url='home'),
        name='sap-analytics'),
    url('update_profile/',
        login_required(views.AdminProfileView.as_view(), login_url='home'),
        name='sap-admin_profile'),
    url('message_board/',
        login_required(views.MessageBoardView.as_view(), login_url='home'),
        name='sap-message_board'),

]
