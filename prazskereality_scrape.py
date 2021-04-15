import time

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
  'Bezbariérový': 'barrier_free',
  'Patro': 'floor',
  'Energetická nárocnost budovy': 'penb',
  'Terasa': 'terrace'
}
URL_BASE = 'https://www.prazskereality.cz'
BOOL_FEATURES = ['equipment', 'basement', 'elevator', 'barrier_free']
MAIN_URL = f'{URL_BASE}/byty-na-prodej/praha'


def get_apartment_links(url):
  soup = BeautifulSoup(requests.get(url).content, "html.parser")
  offers = []
  while (True):
    for offer in soup.select('div.results-list-item'):
      lnk = offer.find("a").attrs.get("href")
      offers.append(f'{URL_BASE}{lnk}')
    next_btn = soup.select_one('a.btn-next')
    # there is no next page
    if (not next_btn):
      break
    next_page_lnk = URL_BASE + next_btn.attrs.get('href')
    soup = BeautifulSoup(requests.get(next_page_lnk).content, "html.parser")

  return offers


def find_in_table(par_table, heading):
  head_elem = par_table.find('dt', text=heading)
  if head_elem:
    return head_elem.next_sibling.get_text()
  return None


def scrape_apartment(apart_url):
  print(f'Scraping apartment: {apart_url}')
  apart = {}

  apart_page = BeautifulSoup(requests.get(apart_url).content, 'html.parser')

  apart['link'] = apart_url
  address_field = apart_page.select_one('div.main-description > h1 > p')
  # some links are
  if not address_field:
    return None
  apart['title'] = str(address_field.previous_sibling)
  apart['address'] = address_field.get_text()
  apart['description'] = apart_page.select_one('div.main-info').get_text()

  par_table = apart_page.select_one('div.main-parameters')

  for k, v in PAR_TBL_HEADINGS.items():
    apart[v] = find_in_table(par_table, k)

  apart = {k: v.strip() for (k, v) in apart.items() if isinstance(v, str)}

  # bool features
  for f in BOOL_FEATURES:
    apart[f] = True if f in apart.keys() and apart[f].lower() == "ano" else False

  return apart


def count_features():
  all_features = []
  apart_links = get_apartment_links(MAIN_URL)
  for link in apart_links:
    apart_page = BeautifulSoup(requests.get(link).content, 'html.parser')
    parameters_div = apart_page.select_one('div.main-parameters')
    if parameters_div:
      f_elems = parameters_div.find_all('dt')
      features = [f.get_text() for f in f_elems]
      all_features = all_features + features

  return Counter(all_features)


aparts = []
apart_links = get_apartment_links(MAIN_URL)
for link in apart_links:
  a = scrape_apartment(link)
  if a:
    aparts.append(a)
aparts_df = pd.DataFrame(aparts)
aparts_df.to_csv("data/prazskereality_prague.csv")
