import os
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

CHR_OPTS = Options()
CHR_OPTS.add_argument('--headless')
CHR_OPTS.add_argument('--no-sandbox')
CHR_OPTS.add_argument('--disable-dev-shm-usage')

DEBUG = bool(int(os.getenv('DEBUG')))

MAIN_URL = 'https://www.sreality.cz/hledani/prodej/byty/praha?'
DEBUG_URL = 'https://www.sreality.cz/hledani/prodej/byty/praha-4?cena-od=0&cena-do=4000000&'
### parametry
def najdi_parameter(parameter): #parameter = hodnota labelu v tabulce
    hodnotaParametru=''
    try:
        for el in page_soup.find('label' , string=parameter).next_sibling(): # pro kazdy label najdi next siblink (hodnota)
            hodnotaParametru = hodnotaParametru + el.get_text().strip() # v nekterych pripadech je hodnota rozdelena v DOME do vice childu siblinku
            # pokud je X nebo fajka
            if 'icon-cross' in str(el): hodnotaParametru = False
            if 'icon-ok' in str(el):    hodnotaParametru = True
    except:
        hodnotaParametru= 'null'
    #m2 se zobrazovali jako m22, kvuli strukture DOMu, tak je odstranime
    if ((hodnotaParametru=='null') or (hodnotaParametru == False) or (hodnotaParametru == True)): return hodnotaParametru
    elif ((parameter=='Lodžie:') or (parameter=='Užitná plocha:') or (parameter=='Plocha podlahová:') or (parameter=='Sklep:')): hodnotaParametru = hodnotaParametru[:-1]
    return hodnotaParametru

def zparsuj_popis():
    popis=''
    for p in page_soup.select('div.description'):
        popis= popis + p.get_text().strip()
    return popis

# converts price to integer
def fix_price(row):
    cut_currency =  row[:-3]
    return cut_currency.replace('\xa0', '')

# converts area to meters as integer
def get_meters(row):
    metry_cislo = re.search(r'^([0-9]+)', row)
    return int(metry_cislo.group(1)) if metry_cislo else ""

# extracts region
def get_region(row):
    if 'Praha' in str(row):
        kraj = row.split(' - ')[-1]
    return kraj

# extracts city
def get_city(row):
    if 'Praha' in str(row):
        city = 'Praha'
    return city

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
            row = 'nan'
    return row

def get_floor(row):
    floor = re.search(r'^(-?\d+)\..*', row)
    return floor.group(1) if floor else None

def clean_dataset(df):
    df['area'] = df['area'].apply(get_meters)
    df['city_part'] = df['address'].apply(get_region)
    df['price'] = df['price'].apply(fix_price)
    df['city'] = df['address'].apply(get_city)
    df['street'] = df['address'].apply(get_street)
    df['size'] = df['title'].apply(get_size)
    df['elevator'] = df['elevator'].apply(clean_elevator)
    df['basement']= df['basement'].apply(clean_basement)
    df['penb'] = df['penb'].apply(get_penb)
    df['floor'] = df['floor'].apply(get_floor)

print('Running webdriver...')
driver = webdriver.Chrome(options=CHR_OPTS)
#Ziskani pocet stranek
nextPageExists= True
propertyLinks= []
i=1
while True:
    print(f'Scraping page: {i}')
    prefix = DEBUG_URL if DEBUG else MAIN_URL
    url = f'{prefix}strana={i}'  # Otevri URL hledani bytu
    driver.get(url)  # otevri v chromu url link
    time.sleep(6)
    page_soup = BeautifulSoup(driver.page_source, 'lxml')  # page_soup pro beautifulsoup nacte html otevrene stanky
    title_elem = page_soup.select('a.title')
    if not title_elem:  # Pokud na stracne existuje nazev inzeratu obsahujici href na inzerat
        break  # pokud na strance odkaz na inzerat neexistuje ukonci cyklus
    for link in title_elem:  # projdi kazdy a.title
        propertyLinks.append('https://sreality.cz' + link.get('href'))  # uloz odkaz na inzerat
    i = i + 1

propertyLinks = list( dict.fromkeys(propertyLinks) ) # odstan duplicity
print(f'Found {len(propertyLinks)} apartments in {i} pages')
### setup
properties = []
# Přiřaď nemovitosti atribut
for i in range(len(propertyLinks)): # projdi kazdy link
    apart = {}
    url = propertyLinks[i]
    print(f'[{i+1}/{len(propertyLinks)}] Scraping apartment: {url}')
    driver.get(url) # otevri link
    # wait for page to load
    max_tries = 10
    j = 0
    while j < max_tries:
        time.sleep(2)
        page_soup = BeautifulSoup(driver.page_source, 'lxml')
        if page_soup.select_one('div.property-title'): # test by selecting element
            break
        j = j + 1
    if j == max_tries:
        break # if max tries reached - skip apartment

    apart['title'] =            page_soup.select_one('div.property-title > h1 > span > span').get_text()
    apart['address'] =          page_soup.select_one('span.location-text').get_text()
    apart['area'] =             najdi_parameter('Užitná plocha:')
    apart['floor_area']=        najdi_parameter('Plocha podlahová:')
    apart['price']=             page_soup.select_one('span.norm-price').get_text()
    apart['description'] =      zparsuj_popis()
    apart['basement'] =         najdi_parameter('Sklep:')
    apart['building_type']=     najdi_parameter('Stavba:')
    apart['penb'] =             najdi_parameter('Energetická náročnost budovy:')
    apart['floor'] =            najdi_parameter('Podlaží:')
    apart['state'] =            najdi_parameter('Stav objektu:')
    apart['internet'] =         najdi_parameter('Telekomunikace:')
    apart['equipment'] =        najdi_parameter('Vybavení:')
    apart['elevator'] =         najdi_parameter('Výtah:')
    apart['parking'] =          najdi_parameter('Parkování:')
    apart['electricity'] =      najdi_parameter('Elektřina:')
    apart['link'] =             propertyLinks[i]
    apart['gas'] =              najdi_parameter('Plyn:')
    apart['loggia'] =           najdi_parameter('Lodžie:')
    apart['umistneni_objektu'] =najdi_parameter('Umístění objektu:')
    apart['doprava'] =          najdi_parameter('Doprava:')
    apart['voda'] =             najdi_parameter('Voda:')
    apart['odpad'] =            najdi_parameter('Odpad:')
    properties.append(apart)

df = pd.DataFrame(properties)
df = df.dropna(subset = ['price'])
df = df.drop(df[df['price'] == 'Info o ceně u RK'].index)
clean_dataset(df)

df.to_csv(os.getenv("OUT_FILEPATH"), index = False)

driver.quit()