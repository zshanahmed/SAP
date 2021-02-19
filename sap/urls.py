from django.urls import path
from . import views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.Home.as_view(), name = 'home'),

    url(r'^dashboard/$',
        views.AlliesListView.as_view(),
        #login_required(views.AlliesListView.as_view(), login_url='login'),  # TODO: Need to specify the proper name for login_url parameter once
        # Zeeshan decides on it
        name='sap-dashboard'),

]
