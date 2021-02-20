import pytest

from pytest_bdd import scenarios, given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

localhost = 'http://127.0.0.1:8000/'

# Scenarios
scenarios('../features/login.feature')

#Fixtures
@pytest.mark.usefixtures('chromeBrowser')

# Given Step
@given('that I am on the login page')
def visit_login(chromeBrowser):
    chromeBrowser.get(localhost)

# When step
@when(parsers.parse('I enter my username {username} and password {password}'))
def input_login(chromeBrowser, username, password):
    chromeBrowser.find_element_by_id('id_username').send_keys(username)
    chromeBrowser.find_element_by_id('id_password').send_keys(password, Keys.RETURN)

# Then step
@then(parsers.parse('I should see the page with title {title}'))
def see_dashboard(chromeBrowser, title):
    element = chromeBrowser.find_element_by_tag_name('legend')
    assert element.text == 'Dashboard'
    chromeBrowser.quit()

