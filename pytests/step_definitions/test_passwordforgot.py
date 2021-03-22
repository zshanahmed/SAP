from pytest_bdd import scenarios, given, when, then, parsers
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pytest

scenarios('../features/signup.feature')
localhost = 'http://127.0.0.1:8000/'