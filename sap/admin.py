from django.contrib import admin

from .models import Ally, Post
# Register your models here.


class AllyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['hawk_id', 'user_type', 'works_at', 'year', 'major']}),
    ]


admin.site.register(Ally, AllyAdmin)

admin.site.register(Post)