import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BROWSER = os.environ.get('BROWSER', 'ChromeHeadless')


@pytest.fixture(scope='module')
def browser(request):
    if BROWSER == 'ChromeHeadless':
        options = Options()
        options.add_argument("--headless")
        browser = webdriver.Chrome(options=options)
    else:
        browser = getattr(webdriver, BROWSER)()
    browser.implicitly_wait(3)
    request.addfinalizer(lambda: browser.quit())
    return browser


@pytest.fixture(scope='module')
def server_url(request, live_server):
    if 'CUSTOM_SERVER_URL' in os.environ:
        return os.environ['CUSTOM_SERVER_URL']
    else:
        return live_server.url


@pytest.mark.parametrize(('link_text', 'expected_url'), [(
    'Open Contracting Partnership',
    'https://www.open-contracting.org',
)])
def test_footer_oc4ids(server_url, browser, link_text, expected_url):
    browser.get(server_url)
    footer = browser.find_element_by_id('footer')
    link = footer.find_element_by_link_text(link_text)
    href = link.get_attribute('href')
    assert expected_url in href
