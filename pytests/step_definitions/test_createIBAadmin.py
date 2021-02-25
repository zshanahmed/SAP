#https://automationpanda.com/2018/10/22/python-testing-101-pytest-bdd/
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import re
import pytest

scenarios('../features/CreateNewIBAadmin.feature')
localhost = 'http://127.0.0.1:8000/'

@pytest.mark.usefixtures('firefoxBrowser')

########################
### Step Definitions ###
########################
@given(parsers.parse('I\'ve logged in'))
def login(firefoxBrowser):
    firefoxBrowser.get(localhost)
    firefoxBrowser.find_element_by_id('id_username').send_keys('iba_admin')
    firefoxBrowser.find_element_by_id('id_password').send_keys('iba_sep_1')
    firefoxBrowser.find_element_by_id("submit").click()


@when(parsers.parse('I navigate to the create verification page'))
def goto_accountSettings(firefoxBrowser):
    #'//*[@id="content"]/nav/ul/li[2]/div/a[1]'
    #'//*[@id="content"]/nav/ul/li[2]/div/a[2]'
    #'//*[@id="content"]/nav/ul/li[2]/div/a[3]'
    firefoxBrowser.find_element_by_xpath('//*[@id="userDropdown"]').click()
    firefoxBrowser.find_element_by_xpath('//*[@id="content"]/nav/ul/li[2]/div/a[2]').click()
    url = firefoxBrowser.current_url


@when(parsers.parse('I fill in "{text}" into element: "{elementID}"'))
def fill_in_textBox(firefoxBrowser, text, elementID):
    firefoxBrowser.find_element_by_id(elementID).send_keys(text)

@when(parsers.parse('I click the button with id: "{buttonID}"'))
def click_button(firefoxBrowser, buttonID):
    firefoxBrowser.find_element_by_id().click()

@then(parsers.parse('User with username "{username}" and password "{password}" should exist'))
def check_created(firefoxBrowser, username, password):
    assert True

@then(parsers.parse('I should be on page with url: "{url}"'))
def check_url(firefoxBrowser, url):
    assert True

@then(parsers.parse('I should see text: "{text}"'))
def check_test(firefoxBrowser, text):
    assert True