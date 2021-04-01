"""
Django admin panel site_url/admin displays all the tables listed here
"""
from django.contrib import admin

from .models import Ally
# Register your models here.


class AllyAdmin(admin.ModelAdmin):
    """
    The class to display ally information on admin panel
    """
    fieldsets = [
        (None, {'fields': ['hawk_id', 'user_type', 'works_at', 'year', 'major']}),
    ]


admin.site.register(Ally, AllyAdmin)
