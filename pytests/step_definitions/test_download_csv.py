from pytest_bdd import scenarios, given, when, then, parsers
import pytest, os
from datetime import date
from pathlib import Path

scenarios('../features/download_csv.feature')
localhost = 'http://127.0.0.1:8000/'

@pytest.mark.usefixtures('firefoxBrowser')

########################
### Step Definitions ###
########################

@given(parsers.parse('I am on dashboard logged in as admin'))
def login(firefoxBrowser):
    firefoxBrowser.get(localhost)
    firefoxBrowser.find_element_by_id('id_username').send_keys('iba_admin')
    firefoxBrowser.find_element_by_id('id_password').send_keys('iba_sep_1')
    firefoxBrowser.find_element_by_id("submit").click()

@when(parsers.parse('I click the button with id: "{buttonID}"'))
def click_button(firefoxBrowser, buttonID):
    firefoxBrowser.find_element_by_id(buttonID).click()

@then(parsers.parse('I should have the csv file in my downloads'))
def have_csv(firefoxBrowser):
    today = date.today()
    day = today.strftime("%b-%d-%Y")
    filename = day + "_allies-List.csv"
    ## may need to change for windows
    path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
    assert os.path.isfile(os.path.join(path_to_download_folder,filename))