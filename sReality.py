import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import csv
import os
### selenium setup

# nutne zadat cestu k chromedriveru - ke stazeni zde: https://chromedriver.chromium.org/downloads (dle verze chrome)
# cesta musi byt primo k .exe
chr_opts = Options()
chr_opts.add_argument('--headless')
chr_opts.add_argument('--no-sandbox')
chr_opts.add_argument('--disable-dev-shm-usage')
chromedriver_path= ''
driver = webdriver.Chrome(chromedriver_path,options=chr_opts)
### parametry
def najdi_parameter(parameter): #parameter = hodnota labelu v tabulce
    hodnotaParametru=''
    try:
        for el in page_soup.find('label' , string=parameter).next_sibling(): # pro kazdy label najdi next siblink (hodnota)
            hodnotaParametru = hodnotaParametru + el.get_text() # v nekterych pripadech je hodnota rozdelena v DOME do vice childu siblinku
            # pokud je X nebo fajka 
            if 'icon-cross' in str(el): hodnotaParametru = 'N' 
            if 'icon-ok' in str(el):    hodnotaParametru = 'Y' 
    except:
        hodnotaParametru= 'null'
    #m2 se zobrazovali jako m22, kvuli strukture DOMu, tak je odstranime
    if ((hodnotaParametru=='null') or (hodnotaParametru=='N') or (hodnotaParametru=='Y')): return hodnotaParametru
    elif ((parameter=='Lodžie:') or (parameter=='Užitná plocha:') or (parameter=='Plocha podlahová:') or (parameter=='Sklep:')): hodnotaParametru = hodnotaParametru[:-1]
    return hodnotaParametru

def zparsuj_popis():
    popis=''
    for p in page_soup.select('div.description'):
        popis= popis + p.get_text()
    return popis

#Ziskani pocet stranek
nextPageExists= True
propertyLinks= []
i=1
while nextPageExists:
    #url = 'https://www.sreality.cz/hledani/prodej/byty/praha?velikost=1%2B1&cena-od=0&cena-do=2800000&&strana={}&bez-aukce=1'.format(i) 
    url = 'https://www.sreality.cz/hledani/prodej/byty/praha?velikost=1%2B1&vlastnictvi=osobni&strana={}&bez-aukce=1'.format(i) # Otevri URL hledani bytu
    driver.get(url) # otevri v chromu url link
    time.sleep(3) # pockej 3 vteriny
    page_source=driver.page_source 
    page_soup=BeautifulSoup(page_source,'lxml') # page_soup pro beautifulsoup nacte html otevrene stanky 
    if page_soup.select('a.title'): # Pokud na stracne existuje a class="title" - nazev inzeratu obsahujici href na inzerat
        #Zescrapuj odkazy na nemovitosti
        for link in page_soup.select('a.title'): # projdi kazdy a.title
            propertyLinks.append('https://sreality.cz'+link.get('href')) # uloz odkaz na inzerat 
        i=i+1
    else:
        nextPageExists = False # pokud na strance odkaz na inzerat neexistuje ukonci cyklus

propertyLinks = list( dict.fromkeys(propertyLinks) ) # odstan duplicity

### setup
properties = [] 
# Přiřaď nemovitosti atribut
for i in range(len(propertyLinks)): # projdi kazdy link
    apart = {}
    url = propertyLinks[i] 
    driver.get(url) # otevry link
    time.sleep(2)
    page_source=driver.page_source
    page_soup=BeautifulSoup(page_source,'lxml')
    apart['title'] =            page_soup.select_one('div.property-title > h1 > span > span').get_text()
    apart['lokace'] =           page_soup.select_one('span.location-text').get_text()
    apart['cena']=              page_soup.select_one('span.norm-price').get_text()
    apart['uzitna_plocha'] =    najdi_parameter('Užitná plocha:')
    apart['podlahova_plocha']=  najdi_parameter('Plocha podlahová:')
    apart['stavba']=            najdi_parameter('Stavba:')
    apart['stav_objektu'] =     najdi_parameter('Stav objektu:')
    apart['umistneni_objektu'] =najdi_parameter('Umístění objektu:')
    apart['podlazi'] =          najdi_parameter('Podlaží:')
    apart['lodzie'] =           najdi_parameter('Lodžie:')
    apart['sklep'] =            najdi_parameter('Sklep:')
    apart['parkovani'] =        najdi_parameter('Parkování:')
    apart['doprava'] =          najdi_parameter('Doprdddava:')
    apart['energeticka_narocnost'] = najdi_parameter('Energetická náročnost budovy:')
    apart['vybaveni'] =         najdi_parameter('Vybavení:')
    apart['vytah'] =            najdi_parameter('Výtah:')
    apart['voda'] =             najdi_parameter('Voda:')
    apart['plyn'] =             najdi_parameter('Plyn:')
    apart['elektrina'] =        najdi_parameter('Elektřina:')
    apart['odpad'] =            najdi_parameter('Odpad:')
    apart['telekomunikace'] =   najdi_parameter('Telekomunikace:')
    apart['popis'] =            zparsuj_popis() 
    apart['url'] =              propertyLinks[i]
    properties.append(apart)

#write to CSV
keys = properties[0].keys()
with open('bytysReality.csv', 'w', newline='', encoding = 'utf-8')  as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(properties)

driver.quit()