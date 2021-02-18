from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='sap-home'),
    path('dashboard/', views.dashboard, name='sap-dasboard'),
]