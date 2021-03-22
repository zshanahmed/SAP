import pytest
import pdb

from pytest_bdd import scenarios, given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

localhost = 'http://127.0.0.1:8000/'

# Scenarios
scenarios('../features/admin_edit_ally.feature')

#Fixtures


@pytest.mark.usefixtures('chromeBrowser')
@given(parsers.parse('I have logged in with username {username} and password {password}'))
def login(chromeBrowser, username, password):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('id_username').send_keys(username)
    chromeBrowser.find_element_by_id('id_password').send_keys(password)
    chromeBrowser.find_element_by_id("submit").click()


@when(parsers.parse('I click on edit button correspoding to a row on table'))
def goto_change_password(chromeBrowser):
    url = chromeBrowser.current_url

    table_id = chromeBrowser.find_element(
        By.ID, 'dataTable')
    table_body = table_id.find_element(By.TAG_NAME, "tbody")
    rows = table_body.find_elements(By.TAG_NAME, "tr")
    if len(rows) > 0:
        first_row = rows[0]
        cols = first_row.find_elements(By.TAG_NAME, "td")
        col = cols[-1]
        all_buttons = col.find_elements(By.TAG_NAME, "li")
        edit_button = all_buttons[1].find_element(By.TAG_NAME, "a").click()

    
@then(parsers.parse('I should see the edit profile page with information of that Ally'))
def goto_change_password(chromeBrowser):
    url = chromeBrowser.current_url
    if 'allies' in url:
        head_text = chromeBrowser.find_element(By.TAG_NAME, "h1").text
        assert head_text == 'Edit Ally Profile'
