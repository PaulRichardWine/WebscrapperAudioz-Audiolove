import requests
from bs4 import BeautifulSoup
import re
from rows_generator import rows_generator
import time

def find_urls(strings):
    '''Wyszukaj wszystkie adresy URL z tekstu i zapisz w liście'''

    urls = []
    for string in strings:
        found_urls = re.findall(r'https?://\S+', string)
        urls.extend(found_urls)
    return urls

def get_hosting_url (url, password):


    headers = {
        "Cookie": "PHPSESSID=65gpf00al9qm647pg4s8mdq8f4; PlayerColorRed=79; PlayerColorGreen=81; PlayerColorBlue=94; PlayerColor=4F515E; dle_user_id=59924; dle_password=a9d242be0bfa72eff975fbc267f34bb0; dle_newpm=0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    }

    # Wyślij zapytanie POST z danymi formularza i nagłówkami
    response = requests.post(url,  headers=headers)
    # response = requests.get(url)

    # Parsowanie HTML za pomocą BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Wybieranie elementu <article> o klasie "articless"
    article_element = soup.find('article', class_='articless')

    text_elements = article_element.find_all_next(string=True)

    # Tworzenie listy adresów URL
    urls = find_urls(text_elements)

    # Wyświetlenie listy adresów URL
    print(urls)

    return urls

# g = rows_generator("audiolove_new.sqlite", "middle")
#
# g_list = list(g)
# for row in g_list:
#     print (row[0])
#     print (row["url"])
#     print (get_hosting_url(row["url"], None))
#     print (".................... \n")
#     time.sleep(3)