import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

PAR_TBL_HEADINGS = {
  'Dispozice:': 'size',
  'Plocha:': 'area',
  'Cena:': 'price',
  'Město:': 'city',
  'Městská část:': 'city_part',
  'Typ vlastnictví:': 'owner',
  'Typ budovy:': 'building_type',
  'PENB:': 'penb',
  'Vybavenost:': 'equipment',
  'Podlaží:': 'floor',
  'Balkón:': 'balcony',
  'Terasa:': 'terrace',
  'Sklep:': 'basement',
  'Stav:': 'state',
  'Lodžie:': 'loggia',
  'Výtah:': 'elevator',
  'Garáž:': 'garage'
}
BS_PARSER = 'lxml'
URL_BASE = 'https://www.bezrealitky.cz'
MAIN_URL = f'{URL_BASE}/vypis/nabidka-prodej/byt/praha'
DEBUG_URL = f'{URL_BASE}/vypis/nabidka-prodej/byt/praha/praha-hostivar'

CHR_OPTS = Options()
CHR_OPTS.add_argument('--headless')
CHR_OPTS.add_argument('--no-sandbox')
CHR_OPTS.add_argument('--disable-dev-shm-usage')


def find_in_table(table, heading):
  head_elem = table.find('th', text=heading)
  if head_elem:
    return table.find('th', text=heading).next_sibling.next_sibling.get_text()
  return None


def scrape_apartment(apart_url):
  apart = {}

  apart_page = BeautifulSoup(requests.get(apart_url).content, 'lxml')

  apart['link'] = apart_url
  apart['title'] = apart_page.select_one('h1.heading__title > span:nth-child(1)').get_text()
  apart['address'] = apart_page.select_one('h1.heading__title > span:last-child').get_text()

  par_table = apart_page.find('h2', text='Parametry').next_sibling.next_sibling

  for k, v in PAR_TBL_HEADINGS.items():
    apart[v] = find_in_table(par_table, k)

  apart['description'] = apart_page.select_one('p.b-desc__info').get_text()

  # strip all features
  for k, v in apart.items():
    if isinstance(v, str):
      apart[k] = v.strip()

  if not apart['price']:
    return None

  apart['address'] = apart['address'].split('\n')[0]
  apart['area'] = get_meters(apart['area'])
  apart['price'] = fix_price(apart['price'])
  apart['street'] = get_street(apart['address'])
  # use Novostavba: bool feature if state is missing
  new_bool = find_in_table(par_table, "Novostavba:") == "Ano"
  apart['state'] = 'novostavba' if not apart['state'] and new_bool else apart['state']

  return apart


def get_apartment_links(debug):
  url = DEBUG_URL if debug else MAIN_URL
  apart_links = []

  i_page = 0
  while True:
    print(f'Scraping page: {i_page}')
    page_url = f'{url}?page={i_page}' if i_page > 0 else url  # first page does not have page GET parameter
    soup = BeautifulSoup(requests.get(page_url).content, BS_PARSER)
    ap_list_elem = soup.select('a.product__link')
    if not ap_list_elem:
      break  # no more apartments to scrape
    for link in ap_list_elem:
      apart_links.append(f'{URL_BASE}{link.get("href")}')  # scrape apartment listing links
    i_page = i_page + 1

  # remove showcase houses
  apart_links = [l for l in apart_links if not 'nove-bydleni' in l]

  apart_links = list(dict.fromkeys(apart_links)) # remove duplicates

  print(f'Found {len(apart_links)} apartments')
  return apart_links


def get_meters(row):
  metraz = row.split(',')[-1].strip()
  metry_cislo = re.search(r'(\d+)', metraz)
  return int(metry_cislo.group(1)) if metry_cislo else None


def fix_price(row):
  cut_currency = row.split(' ')[0]
  return int(cut_currency.replace('.', ''))


def get_street(row):
  street = re.search(r'(.*),.*', row)
  return street.group(1) if street else None


def bezrealitky_scrape(debug=False):
  aparts = []
  apart_links = get_apartment_links(debug)
  for i, link in enumerate(apart_links):
    print(f'[{i + 1}/{len(apart_links)}] Scraping apartment: {link}')
    aparts.append(scrape_apartment(link))
  aparts_df = pd.DataFrame(aparts)
  aparts_df['source'] = 'bezrealitky'
  return aparts_df