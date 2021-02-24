#https://automationpanda.com/2018/10/22/python-testing-101-pytest-bdd/
from pytest_bdd import scenarios, given, when, then, parsers
import pytest


scenarios('../features/CreateNewIBAadmin.feature')
localhost = 'http://127.0.0.1:8000/'

@pytest.mark.usefixtures('firefoxBrowser')

########################
### Step Definitions ###
########################
@given(parsers.parse('I\'ve login with the following credentials: "{credentials}"'))
def login(firefoxBrowser, credentials):
    pass

@when(parsers.parse("I navigate to the account settings page"))
def goto_accountSettings(firefoxBrowser):
    pass

@when(parsers.parse('I fill in "{text}" into element: "{elementID}"'))
def fill_in_textBox(firefoxBrowser, text, elementID):
    pass

@when(parsers.parse('I click the button with id: "{buttonID}"'))
def click_button(firefoxBrowser, buttonID):
    pass

@then(parsers.parse('I should be on the Create IBA Admin Page'))
def check_on_accountSettings(firefoxBrowser):
    assert True

@given(parsers.parse('I\'m on the Create IBA Admin Page'))
def goto_CreateIBAadmin(firefoxBrowser):
    pass

@then(parsers.parse('User with username "{username}" and password "{password}" should be in the database'))
def check_created(firefoxBrowser, username, password):
    assert True