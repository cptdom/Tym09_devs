import re
import time
from collections import Counter
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import numpy as np

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
  'Internet': 'internet'
}

# in this case some features are bool, some strings > bool
MIXED_BOOL_FEATURES = ['balcony', 'terrace']
# bool only features - either True (checkmark) or missing
BOOL_FEATURES = ['basement', 'internet', 'elevator']

CHR_OPTS = Options()
CHR_OPTS.add_argument('--headless')
CHR_OPTS.add_argument('--no-sandbox')
CHR_OPTS.add_argument('--disable-dev-shm-usage')

URL_BASE = 'https://reality.idnes.cz'
MAIN_URL = f'{URL_BASE}/s/prodej/byty/praha/'
DEBUG_URL = f'{URL_BASE}/s/prodej/byty/1+kk/cena-nad-5000000/praha/'  # 127 results


def find_parameter(page_soup, parameter):  # parameter = hodnota labelu
  head_elem = page_soup.find('dt', text=parameter)
  if head_elem:
    next_elem = head_elem.next_sibling.next_sibling
    span = next_elem.find('span')
    if span:  # has icon check/X
      return 'icon--check' in span.attrs.get('class')  # True if checkmark otherwise False
    return next_elem.get_text().strip()  # return parameter text value
  return None


def get_apartment_links(debug):
  print('Running webdriver...')

  url = DEBUG_URL if debug else MAIN_URL
  apart_links = []

  i_page = 0
  while True:
    driver = webdriver.Chrome(options=CHR_OPTS)
    print(f'Scraping page: {i_page}')
    page_url = f'{url}/?page={i_page}' if i_page > 0 else url  # first page does not have page GET parameter
    driver.get(page_url)
    time.sleep(6)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    ap_list_elem = soup.select('a.c-list-products__imgs')
    if not ap_list_elem:
      break  # no more apartments to scrape
    for link in ap_list_elem:
      apart_links.append(f'{URL_BASE}{link.get("href")}')  # scrape apartment listing links
    i_page = i_page + 1
    driver.quit()

  apart_links = list(dict.fromkeys(apart_links))  # Remove duplicates
  print(f'Found {len(apart_links)} apartments')

  return apart_links


def scrape_apartment(apart_url):
  apart = {}

  page_soup = BeautifulSoup(requests.get(apart_url).content, 'lxml')

  apart['link'] = apart_url

  title_elem = page_soup.select_one('h1.b-detail__title > span')
  if not title_elem:
    return None  # apartment that went missing after scraping list of apartments

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

  if not apart['price'] or apart['price'] == 'Cena na vyžádání':
    return None

  apart['area'] = get_meters(apart['area'])
  apart['price'] = fix_price(apart['price'])
  apart['size'] = get_size(apart['title'])
  apart['street'] = get_street(apart['address'])
  apart['city_part'] = get_city_part(apart['address'])
  apart['city'] = get_city(apart['address'])
  apart['floor'] = get_floor(apart['floor'])
  apart['floor_max'] = get_floor_max(apart['floor_max'])

  return apart


def count_features(apart_links):
  all_features = []
  for link in apart_links:
    print(f'Getting features from apartment: {link}')
    apart_page = BeautifulSoup(requests.get(link).content, 'lxml')
    f_elems = apart_page.find_all('dt')
    features = [f.get_text() for f in f_elems]
    all_features = all_features + features

  return Counter(all_features), apart_links


def get_meters(row):
  metry_cislo = re.search(r'(\d+)', str(row))
  return int(metry_cislo.group(1)) if metry_cislo else ""


def fix_price(row):
  cut_currency = ''.join(row.split(' ')[0:-1])
  return int(cut_currency.replace('.', ''))


def get_size(row):
  size = re.search(r'\d\+[\w\d]+', row)
  return size[0] if size else None


def get_street(row):
  street = row.split(',')
  if street is not None:
    if 'Praha' in str(street[0]):
      street = None
    else:
      street = street[0]
  return street


def get_city_part(row):
  city_part = row.split(' - ')
  if city_part is not None:
    if 'okres' in str(city_part[-1]) or 'Praha' in str(city_part[-1]):
      city_part = city_part[-1].split(',')[0]
    else:
      city_part = city_part[-1]
  return city_part


def get_city(row):
  if 'Praha' in str(row):
    city = 'Praha'
  else:
    city = np.nan
  return city


def get_floor(row):
  if not row:
    return None
  if 'přízemí' in row:
    return '0'
  floor = re.search('(\d+)\..*', row)
  return floor.group(1) if floor else None


def get_floor_max(row):
  fm = re.search('(\d+).*', str(row))
  return fm.group(1) if fm else None


def idnes_scrape(debug=False):
  apart_links = get_apartment_links(debug)
  aparts = []
  for i, link in enumerate(apart_links):
    print(f'[{i + 1}/{len(apart_links)}] Scraping apartment: {link}')
    aparts.append(scrape_apartment(link))
  aparts = [a for a in aparts if a]  # remove None values
  aparts_df = pd.DataFrame(aparts)

  return aparts_df
