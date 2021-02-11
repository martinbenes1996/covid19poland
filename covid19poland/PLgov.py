
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import numpy as np
import pandas as pd
import re
import requests

def _filename3(file_name):
    try:
        fname = file_name[0].strip()
        dt = datetime(int(fname[:4]), int(fname[4:6]), int(fname[6:8]))
        return dt
    except:
        return None

def _filename2(file_name):
    try:
        fname = [re.findall(r"\d+", s)[0] for s in file_name[:3]]
        dt = datetime(int('20' + fname[2]), int(fname[1]), int(fname[0]))
        return dt
    except:
        return _filename3(file_name)

def _filename(file_name):
    try:
        fname = file_name[0].strip()
        dt = datetime(int(fname[4:-1]), int(fname[2:4]), int(fname[:2]))
        return dt
    except:
        return _filename2(file_name)

URL = 'https://www.gov.pl/web/koronawirus/pliki-archiwalne-wojewodztwa'
PL_names = {
    't02': 'Dolnośląskie',
    't04': 'Kujawsko-Pomorskie',
    't06': 'Lubelskie',
    't08': 'Lubuskie',
    't10': 'Łódzkie',
    't12': 'Małopolskie',
    't14': 'Mazowieckie',
    't16': 'Opolskie',
    't18': 'Podkarpackie',
    't20': 'Podlaskie',
    't22': 'Pomorskie',
    't24': 'Śląskie',
    't26': 'Świętokrzyskie',
    't28': 'Warmińsko-Mazurskie',
    't30': 'Wielkopolskie',
    't32': 'Zachodniopomorskie'
}

PL_nuts = {
    't02': 'PL51',
    't04': 'PL61',
    't06': 'PL81',
    't08': 'PL43',
    't10': 'PL71',
    't12': 'PL21',
    't14': 'PL9',
    't16': 'PL52',
    't18': 'PL82',
    't20': 'PL84',
    't22': 'PL63',
    't24': 'PL22',
    't26': 'PL72',
    't28': 'PL62',
    't30': 'PL41',
    't32': 'PL42'
}

def read_archive():
    
    # parse page
    logging.info('fetching archive')
    page = requests.get(URL)
    logging.info('parsing HTML')
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # get items
    urls = {}
    for f in soup.select('#main-content > a.file-download'):
        
        # parse urls
        file_url = 'https://www.gov.pl%s' % (f['href'])
        # parse date
        fdate = f.text.split('_')
        file_date = _filename(fdate)
        
        # write down
        urls[file_date] = file_url
    
    # parse dates
    dt_format = lambda d: datetime.strftime(d, "%Y-%m-%d")
    dmin,dmax = dt_format(min(urls.keys())), dt_format(max(urls.keys()))
    
    # check miss-scraping
    dates = pd.date_range(start = dmin, end = dmax)
    if any([d not in urls for d in dates]):
        raise Exception("some date miss-scraped")
    logging.info('parsing HTML from %s to %s' % (dmin,dmax))
    
    # 
    df = None
    for k,v in urls.items():
        logging.info('fetching data from %s' % (k))
        
        # fetch data
        x = pd.read_csv(v, encoding = 'CP1252', sep = ';') # encoding = 'mbcs',
        # parse data
        x.columns = ['region','confirmed','confirmed_10K','deaths',
                     'deaths_without_comorbid','deaths_comorbid','teryt_id']
        x = x[1:]
        #print(x)
        x_ = x[['confirmed','deaths','deaths_comorbid']]\
            .replace({np.nan: 0})\
            .astype(int)
        # append region
        x = x_.assign(teryt_id = x.teryt_id, date = k)
        x['NUTS2'] = x.teryt_id.apply(lambda t: PL_nuts[t])
        x['region'] = x.teryt_id.apply(lambda t: PL_names[t])
        #x = x_.assign(region_control = x.region)
        
        # merge
        if df is None: df = x
        else: df = df.append(x)
        
    return df

def archive_deaths():
    # read data
    #x = pd.read_csv("archive.csv")
    x = read_archive()
    x.to_csv("archive.csv", index = False)

    # comorbid
    df_comorbid = pd.DataFrame(x.values.repeat(x.deaths_comorbid, axis=0), columns=x.columns)
    df_comorbid = df_comorbid[['date','region','NUTS2']]
    df_comorbid['comorbid'] = True
    # no comorbid
    x['deaths_no_comorbid'] = x['deaths'] - x['deaths_comorbid']
    df_no_comorbid = pd.DataFrame(x.values.repeat(x.deaths_no_comorbid, axis=0), columns=x.columns)
    df_no_comorbid = df_no_comorbid[['date','region','NUTS2']]
    df_no_comorbid['comorbid'] = False
    # concat
    df = pd.concat([df_comorbid,df_no_comorbid], ignore_index = True)\
        .sort_values(by = ['date','region'])

    # add columns
    df['reported'] = df.date
    df['age'] = df['sex'] = df['place'] = df['NUTS3'] = df['serious'] = None
    df['reliable'] = True
    df = df[['date','age','sex','place','NUTS2','NUTS3','comorbid','serious','reliable','reported']]\
        .reset_index(drop = True)

    # result
    return df

#logging.basicConfig(level = logging.INFO)
#df = archive_deaths()
#print(df)
