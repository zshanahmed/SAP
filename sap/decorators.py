from functools import wraps
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME

from django.shortcuts import resolve_url
from urllib.parse import urlparse
import azuresite.settings as settings
import requests

default_message = 'Unauthorised action.'
unauthenticated_message = 'User already logged in.'

