import requests
from bs4 import BeautifulSoup
import json
import re


# url = "https://audiolove.me/64030-download-image-sounds-classic-hip-hop-297698-free.html"

def get_alfalink(url):
    number = re.search(r"\d+", url).group()


    data = {
        "news_id": number,
        "div_id": "1",
        "action": "show"
    }

    # Nagłówki żądania
    headers = {
        "Cookie": "PHPSESSID=65gpf00al9qm647pg4s8mdq8f4; PlayerColorRed=79; PlayerColorGreen=81; PlayerColorBlue=94; PlayerColor=4F515E; dle_user_id=59924; dle_password=a9d242be0bfa72eff975fbc267f34bb0; dle_newpm=0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    }

    # Adres URL docelowej strony
    url = 'https://audiolove.me/engine/mods/clickme/ajax.php'

    # Wyślij zapytanie POST z danymi formularza i nagłówkami
    response = requests.post(url, data=data, headers=headers)

    # Usuń BOM z tekstu odpowiedzi
    response_text = response.text.strip('\ufeff')

    # Parsowanie JSON
    output_dict = json.loads(response_text)

    # Wyodrębnienie kodu HTML
    html_code = output_dict["html"]

    # Analiza kodu HTML
    soup = BeautifulSoup(html_code, 'html.parser')

    # Wyodrębnienie adresu URL z atrybutu href
    link = soup.a['href']

    return {link:None}

