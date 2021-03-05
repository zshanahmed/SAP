import pytest
import pdb

from pytest_bdd import scenarios, given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

localhost = 'http://127.0.0.1:8000/'

# Scenarios
scenarios('../features/admin_change_password.feature')

#Fixtures
@pytest.mark.usefixtures('chromeBrowser')

@given(parsers.parse('I have logged in with username {username} and password {password}'))
def login(chromeBrowser, username, password):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('id_username').send_keys(username)
    chromeBrowser.find_element_by_id('id_password').send_keys(password)
    chromeBrowser.find_element_by_id("submit").click()


@when(parsers.parse('I goto change password page'))
def goto_change_password(chromeBrowser):
    url = chromeBrowser.current_url
    time.sleep(2) # Awaiting pageload
    chromeBrowser.find_element_by_xpath('//*[@id="userDropdown"]').click()
    chromeBrowser.find_element_by_xpath(
        '//*[@id="content"]/nav/ul/li[2]/div/a[2]').click()
    


@when(parsers.parse('I fill out old password {old_pass} and matching new password {new_pass} and submit'))
def fill_change_pass_form(chromeBrowser, old_pass, new_pass):
    url = chromeBrowser.current_url
    chromeBrowser.find_element_by_id('prev_pass').send_keys(old_pass)
    chromeBrowser.find_element_by_id('new_pass').send_keys(new_pass)
    chromeBrowser.find_element_by_id('repeat_pass').send_keys(new_pass)
    chromeBrowser.find_element_by_xpath(
        "//button[@type='submit']").click()


@then(parsers.parse('I should see the message saying {message}'))
def see_status(chromeBrowser, message):
    url = chromeBrowser.current_url
    element = chromeBrowser.find_element_by_id('status_message')
    assert message in element.text

@then(parsers.parse('I should change password {new_pass} back to old password {old_pass} and the page shows {message}'))
def see_status(chromeBrowser, new_pass, old_pass, message):
    url = chromeBrowser.current_url
    chromeBrowser.find_element_by_id('prev_pass').send_keys(new_pass)
    chromeBrowser.find_element_by_id('new_pass').send_keys(old_pass)
    chromeBrowser.find_element_by_id('repeat_pass').send_keys(old_pass)
    chromeBrowser.find_element_by_xpath(
        "//button[@type='submit']").click()

    element = chromeBrowser.find_element_by_id('status_message')
    assert message in element.text

