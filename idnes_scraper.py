import time
from collections import Counter
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PAR_TBL_HEADINGS = {
  'Užitná plocha': 'area',
  'Konstrukce budovy': 'building_type',
  'Stav bytu': 'state',
  'Stav budovy': 'building_state',
  'Vlastnictví': 'owner',
  'Podlaží': 'floor',
  'Počet podlaží budovy': 'floor_max',
  'Sklep': 'basement',
  'Topení': 'heating',
  'Balkon': 'balcony',
  'Terasa': 'terrace',
  'Lokalita objektu': 'locality',
  'Elektřina': 'electricity',
  'Parkování': 'parking',
  'Plyn': 'gas',
  'Vybavení': 'equipment',
  'Výtah': 'elevator',
  'PENB': 'penb',
  'Internet': 'internet',
  'Roční spotřeba energie': 'annual_electricity'
}

# in this case some features are bool, some strings > bool
MIXED_BOOL_FEATURES = ['balcony']
# bool only features - either True (checkmark) or missing
BOOL_FEATURES = ['basement', 'internet']

### selenium setup
# nutne zadat cestu k chromedriveru - ke stazeni zde: https://chromedriver.chromium.org/downloads (dle verze chrome)
# cesta musi byt primo k .exe
CHR_OPTS = Options()
CHR_OPTS.add_argument('--headless')
CHR_OPTS.add_argument('--no-sandbox')
CHR_OPTS.add_argument('--disable-dev-shm-usage')

URL_BASE = 'https://reality.idnes.cz'
MAIN_URL = f'{URL_BASE}/s/prodej/byty/praha/'
# MAIN_URL = f'{URL_BASE}/s/prodej/byty/1+kk/cena-nad-5000000/praha/' # 120 results
# MAIN_URL = f'{URL_BASE}/s/prodej/byty/1+kk/cena-do-2000000/praha/' # 6 results only

def find_parameter(page_soup, parameter):  # parameter = hodnota labelu
  head_elem = page_soup.find('dt', text=parameter)
  if head_elem:
    next = head_elem.next_sibling.next_sibling
    span = next.find('span')
    if span:  # has icon check/X
      return 'icon--check' in span.attrs.get('class')  # True if checkmark otherwise False
    return next.get_text().strip()  # return parameter text value
  return None


def get_apartment_links(url, debug=False):
  print('Running webdriver...')

  # run headless by default
  driver = webdriver.Chrome('chromium.chromedriver') if debug \
    else webdriver.Chrome('chromium.chromedriver', options=CHR_OPTS)
  nextPageExists = True
  apart_links = []

  driver.get(url)
  while nextPageExists:
    time.sleep(4)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    if soup.select('a.c-list-products__imgs'):  # Pokud na stracne existuje
      # Zescrapuj odkazy na nemovitosti
      for link in soup.select('a.c-list-products__imgs'):
        apart_links.append(f'{URL_BASE}{link.get("href")}')
      try:
        driver.find_element_by_css_selector('a.btn.paging__next').click()
      except:
        nextPageExists = False

  driver.close()
  apart_links = list(dict.fromkeys(apart_links))  # Remove duplicates
  return apart_links


def scrape_apartment(apart_url):
  print(f'Scraping apartment: {apart_url}')
  apart = {}

  page_soup = BeautifulSoup(requests.get(apart_url).content, 'lxml')

  apart['url'] = apart_url

  title_elem = page_soup.select_one('h1.b-detail__title > span')
  if not title_elem:
    return None # apartment that went missing after scraping list of apartments

  apart['title'] = title_elem.get_text()
  apart['address'] = page_soup.select_one('p.b-detail__info').get_text()
  apart['price'] = page_soup.select_one('p.b-detail__price > strong').get_text()
  apart['description'] = page_soup.select_one('div.b-desc > p').get_text()

  for k, v in PAR_TBL_HEADINGS.items():
    apart[v] = find_parameter(page_soup, k)

  for k, v in apart.items():
    if isinstance(v, str):
      apart[k] = v.strip()

  for f in MIXED_BOOL_FEATURES:
    apart[f] = True if apart[f] or isinstance(apart[f], str) else False


  for f in BOOL_FEATURES:
    apart[f] = bool(apart[f])

  return apart


def count_features(apart_links):
  all_features = []
  for link in apart_links:
    print(f'Getting features from apartment: {link}')
    apart_page = BeautifulSoup(requests.get(link).content, 'html.parser')
    f_elems = apart_page.find_all('dt')
    features = [f.get_text() for f in f_elems]
    all_features = all_features + features

  return Counter(all_features), apart_links

# apart_links = list(pd.read_csv('apart_link.csv')['link']) # cached
apart_links = get_apartment_links(MAIN_URL)
aparts = []
properties = []
for link in apart_links:
  aparts.append(scrape_apartment(link))
aparts_df = pd.DataFrame(aparts)
aparts_df.to_csv("data/idnes_prague.csv")
