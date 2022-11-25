from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class MyChromeDriver(webdriver.Chrome):

    def __init__(self, headless=False, maximize=True):

        options = webdriver.ChromeOptions()
        if headless:    
            options.add_argument('--headless')   
        
        webdriver.Chrome.__init__(self, service=ChromeService(ChromeDriverManager().install()), options=options)

        if maximize:
            self.maximize_window()