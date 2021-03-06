"""
This module contains shared fixtures, steps, and hooks.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def chromeBrowser():
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.headless = True
    b = webdriver.Firefox(options=fireFoxOptions)
    b.implicitly_wait(2)
    yield b
    b.quit()


@pytest.fixture
def chromeBrowser():
    options = Options()
    # options.headless = True
    b = webdriver.Chrome(options=options)
    b.implicitly_wait(5)
    yield b
    b.quit()


@pytest.fixture()
def safariBrowser():
    b = webdriver.Safari()
    b.implicitly_wait(10)
    yield b
    b.quit()

@pytest.fixture()
def cleanup():
    yield
    db_cleanup()

def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    print(f'Step failed: {step}')
