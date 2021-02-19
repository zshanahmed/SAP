from django.shortcuts import render
from .models import Ally
from django.urls import reverse
from django.views import generic


# Create your views here.

class Home(generic.RedirectView):
    """
    Homepage. Redirects to login or task list.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if hasattr(self.request, 'user') and self.request.user.is_active:
            return reverse('sap-dashboard')
        else:
            return reverse('login')  # TODO: Need to define login in urls.py or change "login" here to point to login url's name - get from urls.py


class AlliesListView(generic.ListView):
    template_name = 'sap/dashboard.html'
    context_object_name = 'allies_list'

    def get_queryset(self):
        """
        Return the most recently registered 50 allies
        """
        return Ally.objects.order_by('-id')[:50]
