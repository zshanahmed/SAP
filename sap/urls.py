from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

app_name = 'sap'
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='sap/login.html'), name='home'),
    path('logout/', auth_views.LogoutView.as_view(template_name='sap/logout.html'), name='logout'),

    url(r'^dashboard/$',
        login_required(views.AlliesListView.as_view(), login_url='home'),
        name='sap-dashboard'),
]