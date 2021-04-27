"""
Additional Django template methods can be defined here
"""
from datetime import datetime
from django import template

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """
    Returns the value turned into a list.
    """
    return value.split(key)

@register.filter(name='remove')
def remove(value, key):
    """
    returns the value without the key
    """
    return value.replace(key, '')

@register.filter(name='get_class')
def get_class(value):
    """
    returns the name of the django model from a django object
    """
    return value._meta.verbose_name

@register.filter(name='format_date')
def format_date(value):
    """
    Formats a python date time object in a way that moment can convert to local time.
    """
    return datetime.strftime(value, "%Y/%m/%d %H:%M")
