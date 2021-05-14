import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
from collections import Counter

PAR_TBL_HEADINGS = {
  'Cena': 'price',
  'Aktualizace': 'updated',
  'Dispozice': 'size',
  'Užitná plocha': 'area',
  'Forma vlastnictví': 'owner',
  'Typ budovy': 'building_type',
  'Stav': 'state',
  'Vybavení': 'equipment',
  'Balkón': 'balcony',
  'Sklep': 'basement',
  'Výtah': 'elevator',
  'Patro': 'floor',
  'Energetická nárocnost budovy': 'penb',
  'Terasa': 'terrace',
  'Garáž': 'garage'
}
URL_BASE = 'https://www.prazskereality.cz'
MAIN_URL = f'{URL_BASE}/byty-na-prodej/praha'
BS_PARSER = 'html.parser'


def get_apartment_links(url):
  soup = BeautifulSoup(requests.get(url).content, BS_PARSER)
  offers = []
  while True:
    for offer in soup.select('div.results-list-item'):
      lnk = offer.find("a").attrs.get("href")
      offers.append(f'{URL_BASE}{lnk}')
    next_btn = soup.select_one('a.btn-next')
    # there is no next page
    if not next_btn:
      break
    next_page_lnk = URL_BASE + next_btn.attrs.get('href')
    soup = BeautifulSoup(requests.get(next_page_lnk).content, BS_PARSER)

  print(f'Found {len(offers)} apartments')
  return offers


def find_in_table(par_table, heading):
  head_elem = par_table.find('dt', text=heading)
  if head_elem:
    return head_elem.next_sibling.get_text()
  return None


def scrape_apartment(apart_url):
  apart = {}

  apart_page = BeautifulSoup(requests.get(apart_url).content, BS_PARSER)

  apart['link'] = apart_url
  address_field = apart_page.select_one('div.main-description > h1 > p')
  # some links are old > discard
  if not address_field:
    return None
  apart['title'] = str(address_field.previous_sibling)
  apart['address'] = address_field.get_text()
  apart['description'] = apart_page.select_one('div.main-info').get_text()

  par_table = apart_page.select_one('div.main-parameters')

  for k, v in PAR_TBL_HEADINGS.items():
    apart[v] = find_in_table(par_table, k)

  for k, v in apart.items():
    if isinstance(v, str):
      apart[k] = v.strip()

  if not apart['price'] or apart['price'] == 'Info o ceně u RK':
    return None

  apart['area'] = get_meters(apart['area'])
  apart['price'] = fix_price(apart['price'])
  apart['address'] = get_address(apart['address'])
  apart['city_part'] = get_region(apart['address'])
  apart['city'] = get_city(apart['address'])
  apart['street'] = get_street(apart['address'])
  apart['penb'] = get_penb(apart['penb'])

  return apart


def count_features():
  all_features = []
  apart_links = get_apartment_links(MAIN_URL)
  for link in apart_links:
    apart_page = BeautifulSoup(requests.get(link).content, BS_PARSER)
    parameters_div = apart_page.select_one('div.main-parameters')
    if parameters_div:
      f_elems = parameters_div.find_all('dt')
      features = [f.get_text() for f in f_elems]
      all_features = all_features + features

  return Counter(all_features)


def fix_price(row):
  cut_currency = row[:-3]
  return cut_currency.replace('\xa0', '')


def get_meters(row):
  metraz = row.split(',')[-1].strip()
  metry_cislo = re.search(r'(\d+)', metraz)
  return int(metry_cislo.group(1)) if metry_cislo else ""


def get_region(row):
  if 'Praha' in str(row):
    region_street = row.split(' - ')[1]
    region = region_street.split(',')[0]
    return region if region else None
  return None


def get_city(row):
  if 'Praha' in str(row):
    city = 'Praha'
    return city


def get_street(row):
  street = row.split(',')[-1].strip()
  street_name = re.search(r'([\D ]+)\s.*', street)
  return street_name.group(1) if street_name else street


def is_not_nan(string):
  return string == string


def get_penb(row):
  if is_not_nan(row) or row != 'null':
    row = re.findall(r'[A-Z]', str(row))
    if len(row) > 1:
      row = row[0]
    else:
      row = None
  return row


def get_address(row):
  return row.replace('\xa0', ' ')


def prazskereality_scrape():
  aparts = []
  apart_links = get_apartment_links(MAIN_URL)
  # apart_links = ['https://www.prazskereality.cz/v-soucasne-situaci-nabizime-bezne-prohlidky-s-rouskou-a--7358850.html']
  for i, link in enumerate(apart_links):
    print(f'[{i + 1}/{len(apart_links)}] Scraping apartment: {link}')
    aparts.append(scrape_apartment(link))
  aparts = [a for a in aparts if a]  # remove None values
  aparts_df = pd.DataFrame(aparts)
  aparts_df['source'] = 'prazskereality'
  return aparts_df