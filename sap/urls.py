from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='sap/login.html'), name='home'),
    path('logout/', auth_views.LogoutView.as_view(template_name='sap/logout.html'), name='logout'),
    path('dashboard/', views.dashboard, name='sap-dasboard'),
]