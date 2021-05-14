import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re

MAIN_URL = 'https://www.remax-czech.cz/reality/byty/prodej/praha?'
DEBUG_URL = 'https://www.remax-czech.cz/reality/vyhledavani/?regions%5B19%5D%5B19%5D=on&regions%5B19%5D%5B27%5D=on&sale=1&types%5B4%5D=on&'

CHR_OPTS = Options()
CHR_OPTS.add_argument('--headless')
CHR_OPTS.add_argument('--no-sandbox')
CHR_OPTS.add_argument('--disable-dev-shm-usage')

FIND_PARAMETERS = {
  'area': 'Celková plocha:',
  'basement': 'Sklep:',
  'building_type': 'Druh objektu:',
  'penb': 'Energetická náročnost budovy:',
  'floor': 'Číslo podlaží:',
  'floor_max': 'Počet podlaží v objektu:',
  'state': 'Stav objektu:',
  'internet': 'Telekomunikace:',
  'equipment': 'Vybavení:',
  'elevator': 'Výtah:',
  'heating': 'Topení:',
  'electricity': 'Elektřina:',
  'annual_electricity': 'Měrná vypočtená roční spotřeba energie v kWh/m²/rok:',
  'gas': 'Plyn:',
  'loggia': 'Lodžie:',
  'umistneni_objektu': 'Umístění objektu:',
  'doprava': 'Doprava:',
  'voda': 'Voda:',
  'odpad': 'Odpad:',
  'obcanska_vybavenost': 'Občanská vybavenost:',
  'size': 'Dispozice:',
  'owner': 'Vlastnictví:',
  'balcony': 'Balkon:',
  'terrace': 'Terasa:'
}


### parametry
def najdi_parameter(page_soup, parameter):  # parameter = hodnota labelu v tabulce
  head_elem = page_soup.find('div', string=parameter)
  if head_elem:
    next_elem = head_elem.next_sibling.next_sibling
    return next_elem.get_text().strip() if next_elem else None
  return None

# converts price to integer
def fix_price(row):
  cut_currency = row[:-3]
  return cut_currency.replace('\xa0', '')


# converts area to meters as integer
def get_meters(row):
  metry_cislo = re.search(r'^([0-9]+)', row)
  return int(metry_cislo.group(1)) if metry_cislo else ""


# extracts region
def get_city_part(row):
  return re.search(r'.*\–\s*([\w ]+)', row).group(1)


# extracts city
def get_city(row):
  return 'Praha' if 'Praha' in str(row) else row


# extracts street
def get_street(row):
  street = re.search(r'([\w ]+),.*', row)
  return street.group(1) if street else None


# convert Y to true N to false
def clean_elevator(row):
  return row == 'Ano'


def clean_basement(row):
  if row != 'null':
    row = True
  return row


def get_address(row):
  return row.replace('\t', '').replace('ulice ', '').replace(' mapa', '').replace('\n', ' ')

def scrape_apartment(url):
  apart = {}
  page_soup = BeautifulSoup(requests.get(url).content, 'lxml')

  if page_soup.find('h2', text='Nemovitost nenalezena'):  # aparts that disappeared during the scraping process
    return None

  for e in page_soup.findAll('br'):
    e.extract()

  title_elem = page_soup.select_one('h1.pd-header__title')
  apart['title'] = title_elem.contents[0].split(',')[0].strip() if title_elem else None

  apart['link'] = url
  price_elem = page_soup.select_one('div.mortgage-calc__RE-price > p')
  apart['price'] = price_elem.get_text().strip() if price_elem else None
  apart['description'] = page_soup.select_one('div.pd-base-info__content-collapse-inner').get_text().strip()
  apart['address'] = page_soup.select_one('h2.pd-header__address').get_text().strip()

  for index, title in FIND_PARAMETERS.items():
    apart[index] = najdi_parameter(page_soup, title)


  if not apart['price'] or apart['price'] == 'Info o ceně u RK':
    return None

  equipped = najdi_parameter(page_soup, "Vybaveno:") == "Ano"
  apart['equipment'] = True if not apart['equipment'] and equipped else apart['equipment']
  apart['floor'] = re.findall(r'\d', apart['floor'])[0]
  apart['area'] = get_meters(apart['area'])
  apart['address'] = get_address(apart['address'])
  apart['city_part'] = get_city_part(apart['address'])
  apart['price'] = fix_price(apart['price'])
  apart['city'] = get_city(apart['address'])
  apart['street'] = get_street(apart['address'])
  apart['elevator'] = clean_elevator(apart['elevator'])
  apart['basement'] = clean_basement(apart['basement'])

  return apart


def remax_scrape(debug=False):
  print('Running webdriver...')
  # Ziskani pocet stranek
  nextPageExists = True
  propertyLinks = []
  i = 1
  while nextPageExists:
    driver = webdriver.Chrome(options=CHR_OPTS)
    prefix = DEBUG_URL if debug else MAIN_URL
    url = f'{prefix}stranka={i}'  # Otevri URL hledani bytu
    print(f'Scraping page: {i}')
    driver.get(url)  # otevri v chromu url link
    time.sleep(6)  # pockej 6 vterin
    page_soup = BeautifulSoup(driver.page_source, 'lxml')  # page_soup pro beautifulsoup nacte html otevrene stanky
    driver.quit()
    ap_link_elem = page_soup.select('a.pl-items__link')
    if ap_link_elem:  # Pokud na stracne existuje a class="pl-items__link" - odkaz odkazujici na inzerat
      # Zescrapuj odkazy na nemovitosti
      for link in ap_link_elem:  # projdi kazdy a.title
        if 'Rezervace' in str(link): continue
        if 'Prodáno' in str(link): break
        propertyLinks.append('https://www.remax-czech.cz' + link.get('href'))  # uloz odkaz na inzerat
      i = i + 1
    else:
      nextPageExists = False  # pokud na strance odkaz na inzerat neexistuje ukonci cyklus

  propertyLinks = list(dict.fromkeys(propertyLinks))  # odstan duplicity
  print(f'Found {len(propertyLinks)} apartments in {i} pages')

  aparts = []
  # Přiřaď nemovitosti atribut
  for i,link in enumerate(propertyLinks):  # projdi kazdy link
    print(f'[{i + 1}/{len(propertyLinks)}] Scraping apartment: {link}')
    aparts.append(scrape_apartment(link))

  aparts = [a for a in aparts if a]  # remove None values
  aparts_df = pd.DataFrame(aparts)
  aparts_df['source'] = 'remax'

  return aparts_df
