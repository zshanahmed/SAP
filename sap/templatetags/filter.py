"""
Additional Django template methods can be defined here
"""
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
  return value._meta.verbose_name