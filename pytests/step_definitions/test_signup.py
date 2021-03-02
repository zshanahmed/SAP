from pytest_bdd import scenarios, given, when, then, parsers
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