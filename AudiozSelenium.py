from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc


url = "https://audioz.download/software/win/241477-download_stl-tones-tonehub-v1102-202309-incl-keygen-r2r.html"

class CaptchaSolver:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def navigate_to_url(self, url):
        self.driver.get(url)

    def click_captcha_button(self):
        try:
            captcha_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@onclick="checkcaptcha(); grecaptcha.execute(); return false;"]')))
            captcha_button.click()
            return True
        except:
            return False

    def wait_for_download_links(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="DL_Blocks download" and @itemprop="downloadUrl"]')))

    def capture_page_html(self):
        page_html = self.driver.page_source
        return page_html

    def close(self):
        self.driver.quit()


    def solve_captcha_and_get_html(self, url):
        self.navigate_to_url(url)
        if self.click_captcha_button():
            self.wait_for_download_links()
        page_html = self.capture_page_html()
        self.close()
        return page_html

def get_html_using_selenium(url):
    captcha_solver_instance = CaptchaSolver(uc.Chrome())
    html = captcha_solver_instance.solve_captcha_and_get_html(url)
    return html

# Example usage:
if __name__ == "__main__":
    pass