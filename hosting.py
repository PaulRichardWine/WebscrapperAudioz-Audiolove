import requests
from bs4 import BeautifulSoup
import time
from rows_generator import rows_generator

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import subprocess
import sys


def kill_chrome():
    try:
        if sys.platform == "win32":
            subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'])
        elif sys.platform == "linux" or sys.platform == "linux2":
            subprocess.call(['killall', 'chrome'])
        elif sys.platform == "darwin":
            subprocess.call(['killall', 'Google Chrome'])
    except:
        print ("")

waiting_interval_seconds = 3 #czas w którym powinna ci się załadować strona, możesz wydłużyć jeżeli masz wolne połączenie internetowe


class HostingFactory:
    @staticmethod
    def get_hosting_handler(url):
        if "rapidgator.net" in url:
            print ("factory: Rapidgator")
            return Rapidgator(url)

        elif "nitroflare.com" in url:
            print ("factory: Nitroflare")
            return Nitroflare(url)

        elif "katfile.com" in url:
            print("factory: katfile")
            return Katfile(url)

        elif "turbobit.net" in url:
            print("factory: Turbobit")
            return Turbobit(url)

        elif "ddownload.com" in url:
            print("factory: Ddownload")
            return Ddownload(url)

        elif "filecat.net" in url:
            print("factory: Filecat")
            return Filecat(url)

        elif "k2s.cc" in url or "keep2share.cc" in url:
            print ("factory: Keep2share")
            return Keep2share(url)

        elif "tezfiles.com" in url:
            print ("factory: Tezfiles")
            return Tezfiles(url)

        else:
            print ("factory: BaseHosting")
            return BaseHosting(url)  # Domyślnie używa metody bazowej, jeśli żaden hosting nie pasuje


class BaseSelenium:
    def __init__(self, url):
        self.url = url
        self.driver = uc.Chrome()
        self.wait = WebDriverWait(self.driver, waiting_interval_seconds)

    def navigate_to_url(self):
        self.driver.get(self.url)

    def find_file(self):
        pass

    def find_alert(self):
        pass

    def close_driver(self):
        self.driver.quit()
        kill_chrome()



class BaseHosting:
    def __init__(self, url):
        self.url = url
        self.file_found = None
        self.alert_found = None

    def is_active(self):
        """Determine the status of the file based on the presence of file download or file not found alerts."""

        self.check_file_and_alert()

        if self.file_found and not self.alert_found:
            return "active"
        elif not self.file_found and self.alert_found:
            return "deleted"
        elif not self.file_found and not self.alert_found:
            raise ValueError("sprzeczne wyniki - plik nie znaleziony, ale alert nie znaleziony")
        elif self.file_found and self.alert_found:
            raise ValueError("sprzeczne wyniki - plik znaleziony i alert znaleziony")



class Rapidgator_Selenium(BaseSelenium):

    def find_file(self):

        try:
            self.wait.until(
                EC.visibility_of_element_located((By.XPATH, "//strong[contains(text(), 'Pobieranie pliku:')]")))
            print("file found")
            return True
        except:
            print("file not found")
            return False

    def find_alert(self):
        try:
            # Używamy XPath do znalezienia elementu <h3> z określonym tekstem
            self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[text()='404 Nie znaleziono pliku']")))
            print("alert found")
            return True
        except:
            # Jeśli element nie zostanie znaleziony, zwróć False
            print("alert not found")
            return False


class Rapidgator(BaseHosting):

    def check_file_and_alert(self):

        selenium_instance = Rapidgator_Selenium(self.url)
        selenium_instance.navigate_to_url()
        self.file_found = selenium_instance.find_file()
        self.alert_found = selenium_instance.find_alert()
        selenium_instance.close_driver()


class Rapidgator(BaseHosting):
    def check_file_and_alert(self):
        response = requests.get(self.url)
        self.alert_found  = "File not found" in response.text
        self.file_found   =  "Downloading" in response.text




class Nitroflare(BaseHosting):

    def check_file_and_alert(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        button = soup.find('button', {'id': 'slow-download'})
        self.file_found = bool(button)
        self.alert_found = "This file has been removed" in response.text


class Katfile(BaseHosting):
    def check_file_and_alert(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        button = soup.find('a', class_='btn btn-primary m_btn')
        self.file_found = bool(button)
        self.alert_found = "File has been removed" in response.text



class Turbobit(BaseHosting):
    def check_file_and_alert(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        download_block = soup.find('div', {'id': 'download-file-block'})
        self.file_found = bool(download_block)
        self.alert_found = "file was not found" in response.text.lower()



class Ddownload(BaseHosting):
    def check_file_and_alert(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        button = soup.find('button', {'id': 'downloadbtn'})
        self.file_found = bool(button)
        self.alert_found = "File Not Found" in response.text



#do przemyślenia
class Filecat(BaseHosting):
    def check_file_and_alert(self):
        def modify_url(url):
            # Normalize url to ensure it has a trailing slash for consistent processing
            if not url.endswith('/'):
                url += '/'
            base_url = "https://api.filecat.net/file/"
            # Extract the token between the last two slashes
            token = url.rstrip('/').split('/')[-1]
            # Construct the new URL
            new_url = base_url + token
            return new_url

        url = modify_url(self.url)

        response = requests.get(url )
        print (response.text)
        print (response.status_code)
        self.file_found =  response.status_code == 200
        self.alert_found = response.status_code == 400



class Keep2share_Selenium(BaseSelenium):

    def find_file(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "name-file")))
            print ("file found")
            return True
        except:
            # If the element is not found, return False
            print ("file not found")
            return False

    def find_alert(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert.alert-danger")))
            print ("alert found")
            return True
        except:
            # If the element is not found, return False
            print ("alert not found")
            return False

class Keep2share(BaseHosting):

    def check_file_and_alert(self):

        selenium_instance = Keep2share_Selenium(self.url)
        selenium_instance.navigate_to_url()
        self.file_found = selenium_instance.find_file()
        self.alert_found = selenium_instance.find_alert()
        selenium_instance.close_driver()



Tezfiles_Selenium = Keep2share_Selenium

class Tezfiles(BaseHosting):

    def check_file_and_alert(self):

        selenium_instance = Tezfiles_Selenium(self.url)
        selenium_instance.navigate_to_url()
        self.file_found = selenium_instance.find_file()
        self.alert_found = selenium_instance.find_alert()
        selenium_instance.close_driver()




def check_hosting_availability(url):
    hosting_instance = HostingFactory.get_hosting_handler(url)
    is_active = hosting_instance.is_active()
    print(f"URL: {url} is {is_active}")
    return is_active



# rapidgator.net
# Działający: https://rapidgator.net/file/2254cfd8e1fb200e320521b98043b22e
# Skasowany: https://rapidgator.net/file/396c1c0f3cb117d178a638c34a54be7c/
#
# nitroflare.com
# Działający: https://nitroflare.com/view/0A645473FC3CD70/Ben_Osterhouse_Sospiro_Strings_1_5.rar
# Skasowany: https://nitroflare.com/view/E5707D8F592C275/Plugin.Alliance.Kiive.Audio.XTComp.V1.0.0.U2B.MacOS.zip
#
# katfile.com
# Działający: https://katfile.com/czr5gq27va30/BO_Sospiro_Strings_1_5.part1.rar.html
# Skasowany: https://katfile.com/twdgiov42j35/Excite.Audio.Bloom.Bundle.v1.0.1B-TeamCubeadooby.rar.html
#
# turbobit.net
# Działający: https://turbobit.net/lmwfyus3u0di.html
# Skasowany:  https://turbobit.net/ph04cp29jiz2.html?short_domain=turbo.to
# Skasowany: https://turbobit.net/bqxuozit0wdk.html
#
#
# ddownload.com
# Działający: https://ddownload.com/olcehh34c9xu
# Skasowany: https://ddownload.com/yugdlwmd4tbb

# filecat.net
# Działający: https://filecat.net/f/VbSlNF/
# Skasowany: https://filecat.net/f/uduvcH/
#
#
# Keep2share - k2s.cc
# Działający: https://k2s.cc/file/4d67348a6eaa0/strezov-sampling-logotype-200.png
# Skasowany:https://k2s.cc/file/ae5ebb2222275/Sonible_smartEQ_4_v1.0.1.rar
#
# Tezfiles.com
# Działający: https://tezfiles.com/file/d88f858f1412b/strezov-sampling-logotype-200.png
# Skasowany: https://tezfiles.com/file/7ecb003f9706b



# g = rows_generator("audiolove_new.sqlite", "hosting")
# rows_list = list(g)
# for row in rows_list:
#     print (row[0])
#     url = row["url"]
#     check_hosting_availability(url)

