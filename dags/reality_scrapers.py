from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.utils.dates import days_ago
import tempfile

DAG_MAME = 'reality_scrapers_dag'

default_args = {
  'owner': 'airflow',
  'pr_tempfile': '/tmp/pr_data.csv'
}

dag = DAG(
  DAG_MAME,
  default_args=default_args,
  description='Reality scrapers DAG',
  schedule_interval=None,
  start_date=days_ago(2),
  tags=['scraper'],
)

def prazskereality_scrape(out_filename):
  import re
  import pandas as pd
  from bs4 import BeautifulSoup
  import requests

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

  def fix_price(row):
    cut_currency = row[:-3]
    return cut_currency.replace('\xa0', '')

  def get_meters(row):
    metraz = row.split(',')[-1].strip()
    metry_cislo = re.search(r'\d+', metraz)
    return int(metry_cislo.group(0)) if metry_cislo else ""

  def get_region(row):
    if 'Praha' in str(row):
      region_street = row.split(' - ')[1]
      region = region_street.split(',')[0]
    return region

  def get_city(row):
    if 'Praha' in str(row):
      city = 'Praha'
      return city

  def get_street(row):
    street = row.split(',')[-1].strip()
    return street

  def clean_dataset(a_df):
    a_df = a_df.dropna(subset=['price'])
    a_df = a_df.drop(a_df.columns[[0]], axis=1)
    a_df = a_df.drop(a_df[a_df['price'] == 'Info o ceně u RK'].index)
    a_df['area'] = a_df['area'].apply(get_meters)
    a_df['price'] = a_df['price'].apply(fix_price)
    a_df['city_part'] = a_df['address'].apply(get_region)
    a_df['city'] = a_df['address'].apply(get_city)
    a_df['street'] = a_df['address'].apply(get_street)

    return a_df

  aparts = []
  apart_links = get_apartment_links(MAIN_URL)
  for link in apart_links:
    aparts.append(scrape_apartment(link))
  aparts = [a for a in aparts if a]  # remove None values
  aparts_df = pd.DataFrame(aparts)
  aparts_df = clean_dataset(aparts_df)
  aparts_df.to_csv(out_filename)


def print_res(out_filename):
  import pandas as pd
  print(pd.read_csv(out_filename))


prazskereality_scrape_task = PythonVirtualenvOperator(
  task_id='prazskereality_scrape',
  python_callable=prazskereality_scrape,
  requirements=['beautifulsoup4', 'requests'],
  op_kwargs={'out_filename': default_args['pr_tempfile']},
  dag=dag
)

prazskereality_scrape_task2 = PythonVirtualenvOperator(
  task_id='prazskereality_scrape2',
  python_callable=prazskereality_scrape,
  requirements=['beautifulsoup4', 'requests'],
  op_kwargs={'out_filename': default_args['pr_tempfile']},
  dag=dag
)

print_res_task = PythonOperator(
  task_id='print_res',
  python_callable=print_res,
  op_kwargs={'out_filename': default_args['pr_tempfile']},
  dag=dag
)

[prazskereality_scrape_task, prazskereality_scrape_task2] >> print_res_task
# prazskereality_scrape_task >> print_res_task
