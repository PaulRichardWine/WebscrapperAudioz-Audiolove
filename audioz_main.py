import requests
from bs4 import BeautifulSoup
import AudiozSelenium


def get_html(url):
    headers = {

        "cookie": "YSC=D4tpWEbZjbQ; VISITOR_INFO1_LIVE=b-9UlP9Pd5o; VISITOR_PRIVACY_METADATA=CgJQTBIIEgQSAgsMID8%3D; PREF=f4=4000000", # bez logowania
        #"cookie": "PHPSESSID=c7ebe0206b01d5a5d3e593a27ed67193; cf_clearance=y7DO.YffxwaD8htzJuK.cRK4Ps9NL9go_.FTB9Q5HzM-1713890732-1.0.1.1-mM8jTaSqimpYa34zpTG4BRowILIqCg3t8tced4k_V_qM3HQrFxLmzxb70gzfMyeCDIGbk.HkTMXus3j16RvN9w; dle_user_id=CENSORED; dle_password=CENSORED; dle_newpm=0",
        # FOR CODE TO WORK PROPERLY, copy your own cookie containing login and password, like the one above (but it's censored)
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
    }
    response = requests.get(url, headers=headers)
    return response.text


class Audioz:
    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(self.html, 'html.parser')


    def szukaj_przycisku_captha(self):
        buttons = self.soup.find_all('a', onclick=lambda value: value and 'grecaptcha.execute();' in value)
        # Sprawdź, czy znaleziono przyciski
        if buttons:
            print("Znaleziono przycisk captha:")
            for button in buttons:
                print(button)
            return True
        else:
            print("Nie znaleziono przycisku capthy (to dobrze). ")
            return False



    def get_mirror_divs(self):

        # Find all div elements with class "DL_Blocks mirror"
        mirror_divs = list (self.soup.find_all('div', class_='DL_Blocks mirror'))
        mirror_divs2 = list (self.soup.find_all('div', class_='DL_Blocks mirror2'))
        # Find all div elements with class "DL_Blocks download"
        download_divs = list(self.soup.find_all('div', class_='DL_Blocks download'))
        return mirror_divs + mirror_divs2 + download_divs

    def get_link_from_div(self, div):
        link = div.a['href']
        return link

    def get_password_from_div(self, div):
        if 'Peeplink password:' in div.text:
            password = div.text.split('Peeplink password:')[-1].strip()
            return password
        else:
            return None

    def get_links_and_passwords_from_div(self, divs):
        result_dict = {}
        for div in divs:
            link = self.get_link_from_div(div)
            password = self.get_password_from_div(div)
            result_dict[link] = password
        return result_dict


    def main(self):
        divs = self.get_mirror_divs()
        result_dict = self.get_links_and_passwords_from_div(divs)
        return result_dict


def main(url):
    html = get_html(url)
    audioz_no_selenium = Audioz(html)
    captha = audioz_no_selenium.szukaj_przycisku_captha()
    if captha == False:
        return (audioz_no_selenium.main())
    if captha == True:
        print ("captha, starting selenium")
        html_sel = AudiozSelenium.get_html_using_selenium(url)
        audioz_sel = Audioz(html_sel)
        return (audioz_sel.main())


def main_sel(url):

    html_sel = AudiozSelenium.get_html_using_selenium(url)
    audioz_sel = Audioz(html_sel)
    return (audioz_sel.main())




