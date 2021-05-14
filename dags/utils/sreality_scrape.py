import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHR_OPTS = Options()
CHR_OPTS.add_argument('--headless')
CHR_OPTS.add_argument('--no-sandbox')
CHR_OPTS.add_argument('--disable-dev-shm-usage')

FIND_PARAMETERS = {
  'area': 'Užitná plocha:',
  'floor_area': 'Plocha podlahová:',
  'basement': 'Sklep:',
  'building_type': 'Stavba:',
  'penb': 'Energetická náročnost budovy:',
  'floor': 'Podlaží:',
  'state': 'Stav objektu:',
  'internet': 'Telekomunikace:',
  'equipment': 'Vybavení:',
  'elevator': 'Výtah:',
  'parking': 'Parkování:',
  'electricity': 'Elektřina:',
  'gas': 'Plyn:',
  'loggia': 'Lodžie:',
  'owner': 'Vlastnictví:',
  'balcony': 'Balkón:',
  'terrace': 'Terasa:'
}

MAIN_URL = 'https://www.sreality.cz/hledani/prodej/byty/praha?'
DEBUG_URL = 'https://www.sreality.cz/hledani/prodej/byty/praha-4?cena-od=0&cena-do=4000000&'


### parametry
def najdi_parameter(page_soup, parameter):  # parameter = hodnota labelu v tabulce
  hodnotaParametru = ''
  try:
    for el in page_soup.find('label', string=parameter).next_sibling():  # pro kazdy label najdi next siblink (hodnota)
      hodnotaParametru = hodnotaParametru + el.get_text().strip()  # v nekterych pripadech je hodnota rozdelena v DOME do vice childu siblinku
      # pokud je X nebo fajka
      if 'icon-cross' in str(el): hodnotaParametru = False
      if 'icon-ok' in str(el):    hodnotaParametru = True
  except:
    hodnotaParametru = 'null'
  # m2 se zobrazovali jako m22, kvuli strukture DOMu, tak je odstranime
  if (hodnotaParametru == 'null') or (hodnotaParametru == False) or (hodnotaParametru == True):
    return hodnotaParametru
  elif ((parameter == 'Lodžie:') or (parameter == 'Užitná plocha:') or (parameter == 'Plocha podlahová:') or (
          parameter == 'Sklep:')):
    hodnotaParametru = hodnotaParametru[:-1]
  return hodnotaParametru


def zparsuj_popis(page_soup):
  popis = ''
  for p in page_soup.select('div.description'):
    popis = popis + p.get_text().strip()
  return popis


# converts price to integer
def fix_price(row):
  cut_currency = row[:-3]
  return cut_currency.replace('\xa0', '')


# converts area to meters as integer
def get_meters(row):
  metry_cislo = re.search(r'^([0-9]+)', row)
  return int(metry_cislo.group(1)) if metry_cislo else ""


# extracts region
def get_region(row):
  if 'Praha' in str(row):
    kraj = row.split(' - ')[-1]
    return kraj if kraj else None
  return None


# extracts city
def get_city(row):
  if 'Praha' in str(row):
    return 'Praha'
  return None

# extracts street
def get_street(row):
  street = row.split(',')[0]
  return street


# gets size (1+1, 2+1 etc)
def get_size(row):
  size = re.search(r'([\d][\+][\w]+)', row)
  return size.group(1) if size else None


# convert Y to true N to false
def clean_elevator(row):
  if row == 'Y':
    row = True
  elif row == 'N':
    row = False
  else:
    row = row
  return row


def is_not_nan(string):
  return string == string


def clean_basement(row):
  if row != 'null':
    row = True
  return row


def get_penb(row):
  if is_not_nan(row):
    row = re.findall(r'[A-Z]', str(row))
    if len(row) > 1:
      row = row[1]
    else:
      row = None
  return row


def get_floor(row):
  floor = re.search(r'^(-?\d+)\..*', row)
  return floor.group(1) if floor else None

def scrape_apartment(url):
  driver = webdriver.Chrome(options=CHR_OPTS)
  apart = {}
  driver.get(url)  # otevri link
  # wait for page to load
  max_tries = 10
  j = 0
  while j < max_tries:
    time.sleep(2)
    if BeautifulSoup(driver.page_source, 'lxml').select_one('div.property-title'):  # test by selecting element
      break
    j = j + 1
  if j == max_tries:
    return None

  page_soup = BeautifulSoup(driver.page_source, 'lxml')
  driver.quit()

  apart['title'] = page_soup.select_one('div.property-title > h1 > span > span').get_text()
  apart['address'] = page_soup.select_one('span.location-text').get_text()
  apart['price'] = page_soup.select_one('span.norm-price').get_text()
  apart['description'] = zparsuj_popis(page_soup)
  apart['link'] = url

  for index, title in FIND_PARAMETERS.items():
    apart[index] = najdi_parameter(page_soup, title)

  if not apart['price'] or apart['price'] == 'Info o ceně u RK':
    return None

  apart['area'] = get_meters(apart['area'])
  apart['city_part'] = get_region(apart['address'])
  apart['price'] = fix_price(apart['price'])
  apart['city'] = get_city(apart['address'])
  apart['street'] = get_street(apart['address'])
  apart['size'] = get_size(apart['title'])
  apart['elevator'] = clean_elevator(apart['elevator'])
  apart['basement'] = clean_basement(apart['basement'])
  apart['penb'] = get_penb(apart['penb'])
  apart['floor'] = get_floor(apart['floor'])

  return apart

def sreality_scrape(debug=False):
  print('Running webdriver...')
  # Ziskani pocet stranek
  propertyLinks = []
  i = 1
  while True:
    print(f'Scraping page: {i}')
    driver = webdriver.Chrome(options=CHR_OPTS)
    prefix = DEBUG_URL if debug else MAIN_URL
    url = f'{prefix}strana={i}'  # Otevri URL hledani bytu
    driver.get(url)  # otevri v chromu url link
    time.sleep(6)
    page_soup = BeautifulSoup(driver.page_source, 'lxml')  # page_soup pro beautifulsoup nacte html otevrene stanky
    driver.quit()
    title_elem = page_soup.select('a.title')
    if not title_elem:  # Pokud na stracne existuje nazev inzeratu obsahujici href na inzerat
      break  # pokud na strance odkaz na inzerat neexistuje ukonci cyklus
    for link in title_elem:  # projdi kazdy a.title
      propertyLinks.append('https://sreality.cz' + link.get('href'))  # uloz odkaz na inzerat
    i = i + 1

  propertyLinks = list(dict.fromkeys(propertyLinks))  # odstan duplicity
  print(f'Found {len(propertyLinks)} apartments in {i} pages')
  ### setup
  aparts = []
  # Přiřaď nemovitosti atribut
  for i,url in enumerate(propertyLinks):  # projdi kazdy link
    print(f'[{i + 1}/{len(propertyLinks)}] Scraping apartment: {url}')
    aparts.append(scrape_apartment(url))

  aparts = [a for a in aparts if a]  # remove None values
  aparts_df = pd.DataFrame(aparts)
  aparts_df['source'] = 'sreality'
  return aparts_df
