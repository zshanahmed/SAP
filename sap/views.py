from django.shortcuts import render
from .models import Ally, Message
from django.urls import reverse
from django.views import generic
from django.views.generic import TemplateView


# Create your views here.


class AlliesListView(generic.ListView):
    template_name = 'sap/dashboard.html'
    context_object_name = 'allies_list'

    def get_queryset(self):
        """
        Return the most recently registered 50 allies
        """
        return Ally.objects.order_by('-id')[:50]

class AnalyticsView(TemplateView):
    template_name = "sap/analytics.html"

class AdminProfileView(TemplateView):
    template_name = "sap/profile.html"

class AboutPageView(TemplateView):
    template_name = "sap/about.html"

class SupportPageView(TemplateView):
    template_name = "sap/support.html"

class MessageBoardView(generic.ListView):
    model = Message
    template_name = 'sap/message_board.html'
    context_object_name = 'all_posts_list'