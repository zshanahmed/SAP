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
def fill_in_textBox(chromeBrowser, text, elementID):
    chromeBrowser.find_element_by_id(elementID).send_keys(text)

@then(parsers.parse('I should see element with id: "{idElement}"'))
def find(chromeBrowser,idElement):
    try:
        chromeBrowser.find_element_by_id(idElement)
    except NoSuchElementException:
        assert False
    assert True

@when(parsers.parse('I fill in the undergrad form'))
def fill_out_undergrad(chromeBrowser):
    chromeBrowser.find_element_by_id('freshman').click()
    chromeBrowser.find_element_by_id('low-income').click()
    chromeBrowser.find_element_by_id('major').send_keys('biomedical engineering')
    chromeBrowser.find_element_by_id('major').send_keys('major')
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/input[1]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[5]/div/input[1]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[6]/div/input[1]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[7]/div/input[1]').click()
    chromeBrowser.find_element_by_id('submit_new_ally').click()

@when(parsers.parse('I fill in the grad form'))
def fill_out_grad(chromeBrowser):
    chromeBrowser.find_element_by_id('biochemistry').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/input[1]').click()
    chromeBrowser.find_element_by_id('lgbtq').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[4]/div/input[1]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[5]/div/input[1]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[6]/div/input[1]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[7]/div/input[1]').click()
    chromeBrowser.find_element_by_id('submit_new_ally').click()

@when(parsers.parse('I fill in staff form'))
def fill_out_staff(chromeBrowser):
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[1]/div/input[1]').click()
    chromeBrowser.find_element_by_id('howHelp').send_keys('you cannot help me, for I am just a sea sponge')
    chromeBrowser.find_element_by_id('submit_new_ally').click()

@when(parsers.parse('I fill in faculty form'))
def fill_out_faculty(chromeBrowser):
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[6]/div/div[4]/input').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[2]/div/input[1]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[3]/div/input[1]').click()
    chromeBrowser.find_element_by_id('research-des').send_keys('research')
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[6]/div/input[2]').click()
    chromeBrowser.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/form/div[7]/div[7]/div/input[2]').click()
    chromeBrowser.find_element_by_id('submit_new_ally').click()

@then(parsers.parse('I should see text: "{text}"'))
def check_test(chromeBrowser, text):
    assert (text in chromeBrowser.page_source)

@then(parsers.parse('be able to login with username "{username}", and password "{password}"'))
def check_login(firefoxBrowser, username, password):
    firefoxBrowser.get(localhost)
    firefoxBrowser.find_element_by_id('id_username').send_keys(username)
    firefoxBrowser.find_element_by_id('id_password').send_keys(password)
    firefoxBrowser.find_element_by_id("submit").click()
    assert ('Science Alliance Portal' in firefoxBrowser.page_source)
