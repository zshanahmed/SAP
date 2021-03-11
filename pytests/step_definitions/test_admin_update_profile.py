import pytest
import pdb

from pytest_bdd import scenarios, given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

localhost = 'http://127.0.0.1:8000/'

# Scenarios
scenarios('../features/admin_update_profile.feature')

#Fixtures


@pytest.mark.usefixtures('chromeBrowser')
@given(parsers.parse('I have logged in with username {username} and password {password}'))
def login(chromeBrowser, username, password):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('id_username').send_keys(username)
    chromeBrowser.find_element_by_id('id_password').send_keys(password)
    chromeBrowser.find_element_by_id("submit").click()


@when(parsers.parse('I goto update profile page'))
def goto_change_password(chromeBrowser):
    url = chromeBrowser.current_url
    time.sleep(2)  # Awaiting pageload
    chromeBrowser.find_element_by_xpath('//*[@id="userDropdown"]').click()
    chromeBrowser.find_element_by_xpath(
        '//*[@id="content"]/nav/ul/li[2]/div/a[1]').click()


@when(parsers.parse('I fill out new username {new_username} and email {new_email} and submit'))
def fill_change_pass_form(chromeBrowser, new_username, new_email):
    url = chromeBrowser.current_url
    chromeBrowser.find_element_by_id(
        'username').clear()
    chromeBrowser.find_element_by_id(
        'username').send_keys(new_username)
    chromeBrowser.find_element_by_id('exampleInputEmail').clear()
    chromeBrowser.find_element_by_id('exampleInputEmail').send_keys(new_email.strip("'"))
    chromeBrowser.find_element_by_xpath(
        "//button[@type='submit']").click()


@then(parsers.parse('I should see the message saying {message}'))
def see_status(chromeBrowser, message):
    url = chromeBrowser.current_url
    element = chromeBrowser.find_element_by_id('status_message')
    assert message in element.text


@then(parsers.parse('I should change username {new_username} back to old username {username} and the page shows {message}'))
def see_status(chromeBrowser, new_username, username, message):
    url = chromeBrowser.current_url
    chromeBrowser.find_element_by_id(
        'username').clear()
    chromeBrowser.find_element_by_id(
        'username').send_keys(username)
    chromeBrowser.find_element_by_xpath(
        "//button[@type='submit']").click()

    element = chromeBrowser.find_element_by_id('status_message')
    assert message in element.text
