from pytest_bdd import scenarios, given, when, then, parsers
from selenium.common.exceptions import NoSuchElementException
import pytest

scenarios('../features/signup.feature')
localhost = 'http://127.0.0.1:8000/'

@pytest.mark.usefixtures('chromeBrowser')

########################
### Step Definitions ###
########################
@given(parsers.parse('I go to home page'))
def goto_homepage(chromeBrowser):
    chromeBrowser.get(localhost)

@when(parsers.parse('I click the button with id: "{buttonID}"'))
def click_button(chromeBrowser, buttonID):
    chromeBrowser.find_element_by_id(buttonID).click()

@then(parsers.parse('I should be on page with url: "{url}"'))
def check_url(chromeBrowser, url):
    assert url == chromeBrowser.current_url

@given(parsers.parse('I have navigated to sign-up page'))
def goto_signup(chromeBrowser):
    chromeBrowser.get(localhost)
    chromeBrowser.find_element_by_id('sign-up').click()

@when(parsers.parse('I click the radio button with id: "{idButton}"'))
def click_radio(chromeBrowser, idButton):
    chromeBrowser.find_element_by_id(idButton).click()

@when(parsers.parse('I fill in "{text}" into element: "{elementID}"'))
def fill_in_textBox(firefoxBrowser, text, elementID):
    url = firefoxBrowser.current_url
    firefoxBrowser.find_element_by_id(elementID).send_keys(text)

@then(parsers.parse('I should see element with id: "{idElement}"'))
def find(chromeBrowser,idElement):
    try:
        chromeBrowser.find_element_by_id(idElement)
    except NoSuchElementException:
        assert False
    assert True

@then(parsers.parse('I should see text: "{text}"'))
def check_test(firefoxBrowser, text):
    assert (text in firefoxBrowser.page_source)
