from django.shortcuts import render
from .models import Ally
from django.urls import reverse
from django.views import generic


# Create your views here.


class AlliesListView(generic.ListView):
    template_name = 'sap/dashboard.html'
    context_object_name = 'allies_list'

    def get_queryset(self):
        """
        Return the most recently registered 50 allies
        """
        return Ally.objects.order_by('-id')[:50]
