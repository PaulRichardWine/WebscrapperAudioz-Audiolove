import requests
from bs4 import BeautifulSoup
# from DataBaseFunctions import middle_urls_generator



def get_response_no_password (url):
    response = requests.get(url)
    return response

def convert_http_to_https(url):
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    return url

def get_response_password (url_https, password):

    url = url_https
    headers = {
        'Host': 'peeplink.in',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': url_https,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://peeplink.in',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1'
    }
    data = {
        'pwd': password
    }

    response = requests.post(url, headers=headers, data=data)
    return response

def get_response_peeplink(url, password):
    if password == None:
        print ("getting response no_password")
        return (get_response_no_password(url))
    else:
        print ("getting response with password")
        url_https = convert_http_to_https(url)
        return get_response_password(url_https , password)



def extract_divs_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('a', href=True, target="_blank")
    return divs

def filter_divs(divs):
    filtered_divs = [
        div for div in divs
        if 'LSBan' not in div.get('class', []) and div.get('href') != "http://www.enable-javascript.com/"
    ]
    return filtered_divs

def extract_url_from_div(div):
    return div['href']



def get_urls_from_peeplink(html):

    divs_with_links = extract_divs_from_html(html)
    filtered_divs = filter_divs(divs_with_links)
    extracted_links = [extract_url_from_div(div) for div in filtered_divs]
    print ("exctracted links:", extracted_links)
    return extracted_links






def get_hosting_url(url, password):

    response = get_response_peeplink(url, password)

    html = response.text

    lista = get_urls_from_peeplink(html)
    return lista









# g = middle_urls_generator("audioz_new.sqlite")
#
# rows = list(g)
#
# for row in rows:
#
#     print ("...............")
#     print (row['id'])
#     print (row['url'])
#     print (row['password'])