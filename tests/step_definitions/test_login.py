import pytest

from pytest_bdd import scenarios, given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

localhost = 'http://127.0.0.1:8000/'

# Scenarios
scenarios('../features/login.feature')

#Fixtures
@pytest.fixture
def browser():
    b = webdriver.Chrome()
    b.implicitly_wait(10)
    yield b
    b.quit()

# Given Step
@given(parsers.parse('that I am on the login page'))
def visit_login(browser):
    browser.get(localhost)

# When step
@when(parsers.parse('I enter my Username "{username}" and Password "{password}"'))
def input_login(browser, username, password):
    browser.find_element_by_id('id_username').send_keys(username)
    browser.find_element_by_id('id_password').send_keys(password, Keys.RETURN)

# Then step
@then(parsers.parse('I should see the page with title "{title}"'))
def see_dashboard(browser, title):
    element = browser.find_element_by_tag_name('legend')
    assert element.text == 'Dashboard'
    browser.quit()

