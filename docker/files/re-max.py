import os
import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
### selenium setup
debug = False

MAIN_URL = 'https://www.remax-czech.cz/reality/byty/prodej/praha?'
DEBUG_URL = 'https://www.remax-czech.cz/reality/vyhledavani/?regions%5B19%5D%5B19%5D=on&regions%5B19%5D%5B27%5D=on&sale=1&types%5B4%5D=on&'

# nutne zadat cestu k chromedriveru - ke stazeni zde: https://chromedriver.chromium.org/downloads (dle verze chrome)
# cesta musi byt primo k .exe
CHR_OPTS = Options()
CHR_OPTS.add_argument('start-maximized')
CHR_OPTS.add_argument('enable-automation')
CHR_OPTS.add_argument('--disable-infobars')
CHR_OPTS.add_argument('--disable-browser-side-navigation')
CHR_OPTS.add_argument('--disable-gpu')
CHR_OPTS.add_argument('--headless')
CHR_OPTS.add_argument('--no-sandbox')
CHR_OPTS.add_argument('--disable-dev-shm-usage')

### parametry
def najdi_parameter(parameter): #parameter = hodnota labelu v tabulce
    hodnotaParametru=''
    head_elem = page_soup.find('div' , string=parameter)
    if head_elem:
        next = head_elem.next_sibling.next_sibling.get_text().strip()
        hodnotaParametru= next
    else:
        hodnotaParametru= 'null'
    return hodnotaParametru

def zparsuj_popis():
    popis=''
    for p in page_soup.select('div.description'):
        popis= popis + p.get_text()
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
def get_city_part(row):
    return re.search(r'.*\–\s*([\w ]+)\smapa', row).group(1)

# extracts city
def get_city(row):
    if 'Praha' in str(row):
        city = 'Praha'
    return city

# extracts street
def get_street(row):
    street = re.search(r'(^[ulice]+)(\s)([\w ]+)', row)
    if street is not None: 
        street = street.group(3)
    else:
        street = 'nan'
    return street

# convert Y to true N to false
def clean_elevator(row):
    if row == 'Ano':
        row = True
    elif row == 'Ne':
        row = False
    else:
        row = row
    return row 


def clean_basement(row):
    if row != 'null':
        row = True
    return row
        
def clean_dataset(df):
    df['area'] = df['area'].apply(get_meters)
    df['city_part'] = df['address'].apply(get_city_part)
    df['price'] = df['price'].apply(fix_price)
    df['city'] = df['address'].apply(get_city)
    df['street'] = df['address'].apply(get_street)
    df['elevator'] = df['elevator'].apply(clean_elevator)
    df['basement']= df['basement'].apply(clean_basement)

print('Running webdriver...')
driver = webdriver.Chrome(options=CHR_OPTS)
#Ziskani pocet stranek
nextPageExists= True
propertyLinks= []
i=1
while nextPageExists:
    prefix = DEBUG_URL if debug else MAIN_URL
    url = f'{prefix}stranka={i}' # Otevri URL hledani bytu
    print(f'Scraping page: {i}')
    driver.get(url) # otevri v chromu url link
    time.sleep(3) # pockej 3 vteriny
    page_source=driver.page_source
    page_soup=BeautifulSoup(page_source,'lxml') # page_soup pro beautifulsoup nacte html otevrene stanky
    if page_soup.select('a.pl-items__link'): # Pokud na stracne existuje a class="pl-items__link" - odkaz odkazujici na inzerat
        #Zescrapuj odkazy na nemovitosti
        for link in page_soup.select('a.pl-items__link'): # projdi kazdy a.title
            if 'Rezervace' in str(link): continue
            if 'Prodáno' in str(link): break
            propertyLinks.append('https://www.remax-czech.cz'+link.get('href')) # uloz odkaz na inzerat
        i=i+1
    else:
        nextPageExists = False # pokud na strance odkaz na inzerat neexistuje ukonci cyklus
driver.close()
propertyLinks = list( dict.fromkeys(propertyLinks) ) # odstan duplicity
print(f'Found {len(propertyLinks)} apartments in {i} pages')
### setup
# propertyLinks = ['https://www.remax-czech.cz/reality/detail/310428/prodej-bytu-2-1-v-druzstevnim-vlastnictvi-57-m2-praha-6-brevnov']
properties = []
# Přiřaď nemovitosti atribut
for i in range(len(propertyLinks)): # projdi kazdy link
    apart = {}
    url = propertyLinks[i]
    print(f'[{i+1}/{len(propertyLinks)}] Scraping apartment: {url}')
    page_soup = BeautifulSoup(requests.get(url).content, 'lxml')
    for e in page_soup.findAll('br'):
        e.extract()
    #apart['title'] =           page_soup.select_one('h4.property-title > h1 > span > span').get_text().strip()
    #apart['address'] =         page_soup.select_one('span.location-text').get_text().strip()
    apart['area'] =             najdi_parameter('Celková plocha:')
    price_elem = page_soup.select_one('div.mortgage-calc__RE-price > p')
    apart['price'] =            price_elem.get_text().strip() if price_elem else None
    apart['description'] =      page_soup.select_one('div.pd-base-info__content-collapse-inner').get_text().strip()
    apart['basement'] =         najdi_parameter('Sklep:')
    apart['building_type']=     najdi_parameter('Druh objektu:')
    apart['penb'] =             najdi_parameter('Energetická náročnost budovy:')
    apart['floor'] =            najdi_parameter('Číslo podlaží:')
    apart['floor_max'] =        najdi_parameter('Počet podlaží v objektu:')
    apart['state'] =            najdi_parameter('Stav objektu:')
    apart['internet'] =         najdi_parameter('Telekomunikace:')
    apart['equipment'] =        najdi_parameter('Vybavení:')
    apart['elevator'] =         najdi_parameter('Výtah:')
    apart['heating'] =          najdi_parameter('Topení:')
    apart['electricity'] =      najdi_parameter('Elektřina:')
    apart['annual_electricity']= najdi_parameter('Měrná vypočtená roční spotřeba energie v kWh/m²/rok:')
    apart['link'] =             propertyLinks[i]
    apart['gas'] =              najdi_parameter('Plyn:')
    apart['loggia'] =           najdi_parameter('Lodžie:')
    apart['umistneni_objektu'] =najdi_parameter('Umístění objektu:')
    apart['doprava'] =          najdi_parameter('Doprava:')
    apart['voda'] =             najdi_parameter('Voda:')
    apart['odpad'] =            najdi_parameter('Odpad:')
    apart['obcanska_vybavenost']= najdi_parameter('Občanská vybavenost:')
    apart['address'] =          page_soup.select_one('h2.pd-header__address').get_text().strip()
    apart['size']   =           najdi_parameter('Dispozice:')
    properties.append(apart)
df = pd.DataFrame(properties)
df = df.dropna(subset = ['price'])
df = df.drop(df[df['price'] == 'Info o ceně u RK'].index)
df['floor'] = df['floor'].apply(lambda x: re.findall(r'\d', x)[0])
clean_dataset(df)
df.to_csv(os.getenv("OUT_FILEPATH"), index = False)
driver.quit()

