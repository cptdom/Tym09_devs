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
BOOL_FEATURES = ['balcony', 'terrace', 'basement', 'loggia', 'elevator', 'garage']
MAIN_URL = 'https://www.bezrealitky.cz/vyhledat#offerType=prodej&estateType=byt&disposition=&ownership=&construction=&equipped=&balcony=&order=timeOrder_desc&boundary=%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B14.2244355%2C50.1029963%5D%2C%5B14.2265265%2C50.1003919%5D%2C%5B14.2498381%2C50.1034693%5D%2C%5B14.2583441%2C50.0993837%5D%2C%5B14.2544382%2C50.097063%5D%2C%5B14.2609996%2C50.0962906%5D%2C%5B14.2610944%2C50.0870952%5D%2C%5B14.273347%2C50.087619%5D%2C%5B14.2752539%2C50.0810719%5D%2C%5B14.2845716%2C50.0814296%5D%2C%5B14.2850094%2C50.0782609%5D%2C%5B14.2893735%2C50.0771366%5D%2C%5B14.2901916%2C50.073178%5D%2C%5B14.2824327%2C50.0743046%5D%2C%5B14.2772618%2C50.072986%5D%2C%5B14.2785556%2C50.0709193%5D%2C%5B14.2753003%2C50.0730871%5D%2C%5B14.2580521%2C50.0715166%5D%2C%5B14.2587145%2C50.0644236%5D%2C%5B14.2475584%2C50.0622236%5D%2C%5B14.2480852%2C50.0583091%5D%2C%5B14.2572299%2C50.0544227%5D%2C%5B14.262304%2C50.0555304%5D%2C%5B14.2643067%2C50.0523325%5D%2C%5B14.2716323%2C50.0543186%5D%2C%5B14.2726358%2C50.0506112%5D%2C%5B14.2681736%2C50.0486908%5D%2C%5B14.2710433%2C50.0469324%5D%2C%5B14.2700997%2C50.040097%5D%2C%5B14.2872209%2C50.0279596%5D%2C%5B14.2975722%2C50.0235558%5D%2C%5B14.3158709%2C50.0235953%5D%2C%5B14.3114577%2C50.006978%5D%2C%5B14.3007933%2C50.0118141%5D%2C%5B14.30053%2C50.0043801%5D%2C%5B14.2948377%2C50.0022104%5D%2C%5B14.3101029%2C49.993838%5D%2C%5B14.3139615%2C49.9947829%5D%2C%5B14.3181009%2C49.9888928%5D%2C%5B14.3349813%2C49.9938483%5D%2C%5B14.3427557%2C49.9906305%5D%2C%5B14.3353153%2C49.9886648%5D%2C%5B14.3395903%2C49.9807517%5D%2C%5B14.3268139%2C49.9718584%5D%2C%5B14.3461789%2C49.9747107%5D%2C%5B14.344916%2C49.9676279%5D%2C%5B14.3292319%2C49.9648505%5D%2C%5B14.3254392%2C49.9572087%5D%2C%5B14.3428774%2C49.9475842%5D%2C%5B14.3603929%2C49.9474546%5D%2C%5B14.3683756%2C49.9513236%5D%2C%5B14.3768119%2C49.9466207%5D%2C%5B14.3879707%2C49.9497837%5D%2C%5B14.3890496%2C49.9451745%5D%2C%5B14.395562%2C49.9419006%5D%2C%5B14.3942296%2C49.9538976%5D%2C%5B14.4006472%2C49.9706693%5D%2C%5B14.4194183%2C49.9635636%5D%2C%5B14.4386195%2C49.9681197%5D%2C%5B14.4445941%2C49.9738632%5D%2C%5B14.4622402%2C49.9707711%5D%2C%5B14.4663038%2C49.9810366%5D%2C%5B14.4739923%2C49.9804035%5D%2C%5B14.473704%2C49.9837523%5D%2C%5B14.486985%2C49.985687%5D%2C%5B14.4839334%2C49.992419%5D%2C%5B14.5072536%2C49.9974771%5D%2C%5B14.5081846%2C49.9921388%5D%2C%5B14.5137466%2C49.992583%5D%2C%5B14.5300192%2C50.0007153%5D%2C%5B14.520994%2C50.0077216%5D%2C%5B14.5274725%2C50.0108381%5D%2C%5B14.5508521%2C50.0079867%5D%2C%5B14.5542318%2C50.0121564%5D%2C%5B14.5627521%2C50.0115863%5D%2C%5B14.5683172%2C50.0073516%5D%2C%5B14.582393%2C50.0163634%5D%2C%5B14.5817136%2C50.010951%5D%2C%5B14.5944084%2C50.0100508%5D%2C%5B14.5949721%2C50.007143%5D%2C%5B14.6022636%2C50.0094315%5D%2C%5B14.6039007%2C50.0019258%5D%2C%5B14.6078305%2C50.002937%5D%2C%5B14.6103406%2C49.9986363%5D%2C%5B14.6401518%2C49.9944411%5D%2C%5B14.6469229%2C49.9987546%5D%2C%5B14.6382891%2C50.0057827%5D%2C%5B14.6454958%2C50.0047342%5D%2C%5B14.6498044%2C50.0087938%5D%2C%5B14.6577854%2C50.0043495%5D%2C%5B14.6626193%2C50.0084011%5D%2C%5B14.6615855%2C50.0127833%5D%2C%5B14.6685483%2C50.0134346%5D%2C%5B14.669537%2C50.0188407%5D%2C%5B14.6561272%2C50.0309551%5D%2C%5B14.6569571%2C50.0378173%5D%2C%5B14.6668511%2C50.0385277%5D%2C%5B14.6538674%2C50.0492542%5D%2C%5B14.6440386%2C50.0421831%5D%2C%5B14.6402196%2C50.0484131%5D%2C%5B14.6401916%2C50.0568947%5D%2C%5B14.6908607%2C50.0720182%5D%2C%5B14.6999919%2C50.0721289%5D%2C%5B14.7067867%2C50.0870194%5D%2C%5B14.7039175%2C50.0917426%5D%2C%5B14.6886937%2C50.0963003%5D%2C%5B14.6903288%2C50.1006277%5D%2C%5B14.665884%2C50.1026521%5D%2C%5B14.6574355%2C50.1065009%5D%2C%5B14.6591154%2C50.1226041%5D%2C%5B14.6352008%2C50.1239183%5D%2C%5B14.6322995%2C50.1299032%5D%2C%5B14.6086335%2C50.1271149%5D%2C%5B14.6005164%2C50.129523%5D%2C%5B14.5877286%2C50.1452435%5D%2C%5B14.5990028%2C50.1541328%5D%2C%5B14.5632297%2C50.1501702%5D%2C%5B14.5609936%2C50.1615751%5D%2C%5B14.5505391%2C50.1661221%5D%2C%5B14.5342354%2C50.161565%5D%2C%5B14.5305116%2C50.1661902%5D%2C%5B14.5324832%2C50.1771831%5D%2C%5B14.5268551%2C50.1774301%5D%2C%5B14.5069039%2C50.1714361%5D%2C%5B14.4795218%2C50.1722942%5D%2C%5B14.4801495%2C50.1698783%5D%2C%5B14.4669127%2C50.1695438%5D%2C%5B14.4641231%2C50.159923%5D%2C%5B14.4281375%2C50.1576674%5D%2C%5B14.4289771%2C50.1535113%5D%2C%5B14.4200136%2C50.1529649%5D%2C%5B14.4225022%2C50.1498332%5D%2C%5B14.3999734%2C50.1479062%5D%2C%5B14.3991472%2C50.1433746%5D%2C%5B14.3949016%2C50.141429%5D%2C%5B14.3848779%2C50.1469262%5D%2C%5B14.3657001%2C50.1480311%5D%2C%5B14.3541236%2C50.137526%5D%2C%5B14.3574439%2C50.1296478%5D%2C%5B14.3600421%2C50.1295213%5D%2C%5B14.3556407%2C50.1246523%5D%2C%5B14.3607835%2C50.1160189%5D%2C%5B14.3206068%2C50.1152415%5D%2C%5B14.3156962%2C50.1229456%5D%2C%5B14.3158782%2C50.1286167%5D%2C%5B14.3024335%2C50.1300768%5D%2C%5B14.2946854%2C50.1247846%5D%2C%5B14.2971713%2C50.1205942%5D%2C%5B14.2883495%2C50.1162211%5D%2C%5B14.2788382%2C50.1190811%5D%2C%5B14.2500356%2C50.1107913%5D%2C%5B14.2388054%2C50.1117993%5D%2C%5B14.2393227%2C50.1072816%5D%2C%5B14.2244355%2C50.1029963%5D%5D%5D%7D%7D&center=%5B14.465611099999933%2C50.05980988882607%5D&zoom=10.34135876148967&locationInput=Praha%2C%20%C4%8Cesko&limit=15'
DEBUG_URL = 'https://www.bezrealitky.cz/vyhledat#offerType=prodej&estateType=byt&disposition=&ownership=&construction=&equipped=&balcony=&order=timeOrder_desc&boundary=%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B14.4115822%2C50.075668%5D%2C%5B14.4158769%2C50.0618799%5D%2C%5B14.4185628%2C50.0632596%5D%2C%5B14.4243179%2C50.0610467%5D%2C%5B14.426801%2C50.063992%5D%2C%5B14.434502%2C50.0654888%5D%2C%5B14.4368844%2C50.0680983%5D%2C%5B14.4409362%2C50.0664946%5D%2C%5B14.4486268%2C50.0681265%5D%2C%5B14.4426213%2C50.0724109%5D%2C%5B14.4493787%2C50.0735282%5D%2C%5B14.4474519%2C50.0800455%5D%2C%5B14.4396038%2C50.0820922%5D%2C%5B14.4408584%2C50.0852333%5D%2C%5B14.4372665%2C50.086667%5D%2C%5B14.4305145%2C50.0771635%5D%2C%5B14.4213384%2C50.0775755%5D%2C%5B14.4220807%2C50.079161%5D%2C%5B14.4196773%2C50.0792367%5D%2C%5B14.4115822%2C50.075668%5D%5D%5D%7D%7D&center=%5B14.430480450000005%2C50.07385856111608%5D&zoom=14.592915982476153&locationInput=Praha%202%2C%20Praha%2C%20okres%20Hlavn%C3%AD%20m%C4%9Bsto%20Praha%2C%20Hlavn%C3%AD%20m%C4%9Bsto%20Praha%2C%20Praha%2C%20%C4%8Cesko&limit=15'

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

  # bool features
  for f in BOOL_FEATURES:
    apart[f] = True if apart[f] == "Ano" else False

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
  print('Running webdriver...')
  driver = webdriver.Chrome(options=CHR_OPTS)

  driver.get(url)
  time.sleep(30)
  # click 'Show more' until there are no more apartments to load
  while True:
    try:
      time.sleep(10)
      show_more_btn = driver.find_element_by_css_selector('div.b-filter__inner.pb-0 > div.row > div > p > button')
      print('Loading more offers...')
      driver.execute_script("arguments[0].click();", show_more_btn)  # click 'load more' button
    except NoSuchElementException:
      break

  soup = BeautifulSoup(driver.page_source, "lxml")
  driver.quit()

  # collect all links
  links = []
  for offer in soup.find_all('article', class_='product'):
    links.append(offer.find('a').attrs.get('href'))

  # remove showcase houses
  links = [l for l in links if not 'nove-bydleni' in l]

  print(f'Found {len(links)} apartments')
  return links


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