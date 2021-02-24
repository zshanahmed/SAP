import pytest
import pdb

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

@when(parsers.parse('I click on {link}'))
def click_on(chromeBrowser, link):
    chromeBrowser.maximize_window()
    x = chromeBrowser.find_element_by_link_text(link)
    x.click()
 
# Then step
@then(parsers.parse('I should see the page with title {title}'))
def see_dashboard(chromeBrowser, title):
    element = chromeBrowser.find_element_by_tag_name('h1')
    assert element.text == title

# Then step
@then(parsers.parse('I should see a message saying \'{message}\''))
def check_message(chromeBrowser, message):
    print(message)
    element = chromeBrowser.find_element_by_id('login-alert')
    assert element.text == 'Username or password is incorrect!'
    chromeBrowser.quit()
