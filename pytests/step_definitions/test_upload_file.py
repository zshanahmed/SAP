from pytest_bdd import scenarios, given, when, then, parsers
import pytest, os
from datetime import date
from pathlib import Path
import time
import shutil
from selenium.webdriver.common.keys import Keys

scenarios('../features/upload_file.feature')
localhost = 'http://127.0.0.1:8000/'

@pytest.mark.usefixtures('chromeBrowser')


########################
### Step Definitions ###
########################

@given(parsers.parse('I am on dashboard logged in as admin'))
def login(chromeBrowser):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('id_username').send_keys('iba_admin')
    chromeBrowser.find_element_by_id('id_password').send_keys('iba_sep_1')
    chromeBrowser.find_element_by_id("submit").click()
    time.sleep(1)

@when(parsers.parse('I click the button with id: "{buttonID}"'))
def click_button(chromeBrowser, buttonID):
    chromeBrowser.find_element_by_id(buttonID).click()

## Make sure downloads are empty before you run this test.
@then(parsers.parse('I should have the error file in my downloads'))
def have_csv(chromeBrowser):
    today = date.today()
    day = today.strftime("%b-%d-%Y")
    filename = day + "SAP_Upload-log.xlsx"
    ## may need to change for windows
    path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
    time.sleep(1)
    initalFile = max([path_to_download_folder + "/" + f for f in os.listdir(path_to_download_folder)],
                   key=os.path.getctime)
    initial_path = os.path.join(path_to_download_folder, initalFile)
    shutil.move(initial_path, os.path.join(path_to_download_folder, filename))
    time.sleep(1)
    tmp = chromeBrowser.current_url
    chromeBrowser.get(localhost)
    time.sleep(1)
    chromeBrowser.get(tmp)
    time.sleep(1)
    assert os.path.isfile(os.path.join(path_to_download_folder, filename))
    os.remove(os.path.join(path_to_download_folder, filename))

@given(parsers.parse('I have navigated to sign-up page'))
def goto_signup(chromeBrowser):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('sign-up').click()


@when(parsers.parse('I fill in "{text}" into element: "{elementID}"'))
def fill_in_textBox(chromeBrowser, text, elementID):
    chromeBrowser.find_element_by_id(elementID).send_keys(text)

@then((parsers.parse('I should not be able to download users.')))
def check_download(chromeBrowser):
    chromeBrowser.get(localhost + 'download_allies/')
    assert '403' in chromeBrowser.page_source

@then(parsers.parse('I should see text: "{text}"'))
def check_test(chromeBrowser, text):
    assert (text in chromeBrowser.page_source)

@when(parsers.parse('I select file using "{elementID}" with name: "{file}"'))
def addFile(chromeBrowser, elementID, file):

    path = os.path.abspath(file)
    element = chromeBrowser.find_element_by_id(elementID)
    element.send_keys(path)

@when(parsers.parse('I refresh the page'))
def refresh(chromeBrowser):
    chromeBrowser.refresh()

@then(parsers.parse('I should see entries with names: "{name}"'))
def check_if_names_there(chromeBrowser, name):
    table = chromeBrowser.find_element_by_id('dataTable')
    bool_array = []
    ar = []
    names = name.split(", ")
    count = 0
    for row in table.find_elements_by_css_selector('tr'):
        for cell in row.find_elements_by_tag_name('td'):
            if count % 6 == 0:
                ar.append(cell.text)
            count += 1

    print(ar)

    for name in names:
        assert name in ar
