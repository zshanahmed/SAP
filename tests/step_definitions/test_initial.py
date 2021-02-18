#https://automationpanda.com/2018/10/22/python-testing-101-pytest-bdd/
import pytest, platform

from pytest_bdd import scenarios, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

scenarios('../features/initial.feature')

localhost = 'http://127.0.0.1:8000/'

@pytest.fixture
def firefoxBrowser():
    b = webdriver.Firefox()
    b.implicitly_wait(10)
    yield b
    b.quit()

@pytest.fixture
def chromeBrowser():
    b = webdriver.Chrome()
    b.implicitly_wait(10)
    yield b
    b.quit()

@pytest.fixture()
def safariBrowser():
    b = webdriver.Safari()
    b.implicitly_wait(10)
    yield b
    b.quit()

@when(parsers.parse('I\'m on the homepage'))

def first_step(firefoxBrowser, chromeBrowser, safariBrowser):
    browsers = [firefoxBrowser, chromeBrowser]
    if platform.system() == 'Darwin':
        browsers.append(safariBrowser)
    for browser in browsers:
        browser.get(localhost)


@then(parsers.parse('I should see: "{phrase}"'))
def second_step(firefoxBrowser, chromeBrowser, safariBrowser, phrase):
    # https://www.tutorialspoint.com/how-to-get-text-with-selenium-web-driver-in-python
    browsers = [firefoxBrowser, chromeBrowser]
    if platform.system() == 'Darwin':
        browsers.append(safariBrowser)
    for browser in browsers:
        header = browser.find_element_by_css_selector("h1").text
        assert header == phrase