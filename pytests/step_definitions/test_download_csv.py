from pytest_bdd import scenarios, given, when, then, parsers
import pytest, os
from datetime import date
from pathlib import Path
import time
import shutil
from selenium.webdriver.common.keys import Keys

scenarios('../features/download_csv.feature')
localhost = 'http://127.0.0.1:8000/'

@pytest.mark.usefixtures('firefoxBrowser')
@pytest.mark.usefixtures('chromeBrowser')

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
    filename = day + "_ScienceAllianceAllies.csv"
    ## may need to change for windows
    path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
    time.sleep(1)
    initalFile = max([path_to_download_folder + "/" + f for f in os.listdir(path_to_download_folder)],
                   key=os.path.getctime)
    initial_path = os.path.join(path_to_download_folder, initalFile)
    shutil.move(initial_path, os.path.join(path_to_download_folder, filename))
    time.sleep(1)
    assert os.path.isfile(os.path.join(path_to_download_folder, filename))
    os.remove(os.path.join(path_to_download_folder, filename))

@given(parsers.parse('I have navigated to sign-up page'))
def goto_signup(chromeBrowser):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('sign-up').click()

@when(parsers.parse('I click the radio button with id: "{idButton}"'))
def click_radio(chromeBrowser, idButton):
    chromeBrowser.find_element_by_id(idButton).click()

@when(parsers.parse('I enter my username {username} and password {password}'))
def input_login(chromeBrowser, username, password):
    chromeBrowser.find_element_by_id('id_username').send_keys(username)
    chromeBrowser.find_element_by_id('id_password').send_keys(password, Keys.RETURN)

@when(parsers.parse('I fill in staff form'))
def fill_out_staff(chromeBrowser):
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/input[1]').click()
    chromeBrowser.find_element_by_id('howHelp').send_keys('you cannot help me, for I am just a sea sponge')
    chromeBrowser.find_element_by_id('submit_new_ally').click()

@given(parsers.parse('I have logged in'))
def login(chromeBrowser):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('id_username').send_keys("haw2")
    chromeBrowser.find_element_by_id('id_password').send_keys("iba_sep_1")
    chromeBrowser.find_element_by_id("submit").click()

@when(parsers.parse('I fill in "{text}" into element: "{elementID}"'))
def fill_in_textBox(chromeBrowser, text, elementID):
    chromeBrowser.find_element_by_id(elementID).send_keys(text)

@then((parsers.parse('I should not be able to download users.')))
def check_download(chromeBrowser):
    time.sleep(5)
    chromeBrowser.get(localhost + 'download_allies/')
    time.sleep(5)
    assert '403' in chromeBrowser.page_source