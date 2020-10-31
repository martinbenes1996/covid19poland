
import csv
import datetime
from io import BytesIO
import pkg_resources
from zipfile import ZipFile

from bs4 import BeautifulSoup
import pandas as pd
import requests
from waybackmachine import WaybackMachine

from . import offline as offline_module

def _parse_death_table(df, r = 7):
    df = df.iloc[r,2:].reset_index(drop = True)
    df.columns = ["Total"] + [str(i+1) for i in range(12)]
    return df
def _parse_deaths():
    url = {
        2018: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2018_00_7.zip&sys=zgo',
        2017: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2017_00_7.zip&sys=zgo',
        2016: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2016_00_7.zip&sys=zgo',
        2015: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2015_00_7.zip&sys=zgo',
        2014: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2014_00_7.zip&sys=zgo',
        2013: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2013_00_7.zip&sys=zgo',
        2012: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2012_00_7.zip&sys=zgo',
        2011: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2011_00_7.zip&sys=zgo',
        2010: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2010_00_7.zip&sys=zgo'
    }
    data = []
    for y in url:
        # download file
        res = requests.get(url[y])
        zip_file = ZipFile(BytesIO(res.content))
        # parse zip
        files = zip_file.namelist()
        tablerow = 9 if y == 2010 else 7
        # parse male data
        with zip_file.open(files[0], 'r') as xlsfile:
            x  = pd.read_excel(xlsfile, sheet_name="MĘŻCZYŹNI")
            xx = [y, "M"] + _parse_death_table(x, tablerow).tolist()
            data.append(xx)
        # parse female data
        with zip_file.open(files[0], 'r') as xlsfile:
            x  = pd.read_excel(xlsfile, sheet_name="KOBIETY")
            xx = [y, "F"] + _parse_death_table(x, tablerow).tolist()
            data.append(xx)
    data = pd.DataFrame(data, columns = ["Year", "Sex", "Total"] + [str(i+1) for i in range(12)])
    data.to_csv(pkg_resources.resource_filename(__name__, "data/deaths.csv"), index = False)
    return data

def deaths(offline = True):
    if offline:
        try:
            return pd.read_csv(pkg_resources.resource_filename(__name__, "data/deaths.csv"))
        except: pass
    return _parse_deaths()

def covid_death_cases(offline = True):
    if offline is False:
        raise Exception("online twitter parsing is not reliable, use offline data (manually checked)")
    return offline_module.covid_death_cases()

def covid_deaths(level = 3, offline = True):
    x = covid_death_cases(offline = offline)
    
    # rename attributes
    if level == 1: regiongroup = []
    elif level == 2: regiongroup = ["NUTS2"]
    elif level == 3: regiongroup = ["NUTS2","NUTS3"]
    else: raise Exception("level must be one of 1,2,3")
    x['week'] = x.date.apply( lambda dt: dt.isocalendar()[1] )
    
    # age group
    def to_age_group(a):
        try:
            a = int(a)
            return str(a).zfill(2) + "_" + str(a + 4).zfill(2)
        except: return None
    x['age_group'] = x['age'].apply( lambda a: to_age_group((a//5) * 5) )
    
    # group
    xx = x\
        .groupby(['week','age_group','sex',*regiongroup])\
        .size()\
        .reset_index(name='deaths')
    return xx

_nuts2_pl = {
    "dolnoślaskie": "PL51",
    "kujawsko-pomorskie": "PL61",
    "lubelskie": "PL81",
    "lubuskie": "PL43",
    "łódzkie": "PL71",
    "małopolskie": "PL21",
    "mazowieckie": "PL9",
    "opolskie": "PL52",
    "podkarpackie": "PL82",
    "podlaskie": "PL84",
    "pomorskie": "PL63",
    "śląskie": "PL22",
    "świętokrzyskie": "PL72",
    "warmińsko-mazurskie": "PL62",
    "wielkopolskie": "PL41",
    "zachodniopomorskie": "PL42"
    
}
def covid_tests_wayback(end = None, start = None):
    url = 'https://www.gov.pl/web/zdrowie/liczba-wykonanych-testow'
    x = pd.DataFrame(data = None, columns = ["date","region","tests"])
    if end == None:
        end = datetime.datetime(2020,5,12)
    
    for response,version_time in WaybackMachine(url, start = start, end = end):
        _log.info(f"parsing {version_time}")
        # parse HTML
        htmlParse = BeautifulSoup(response.text, features="lxml")
        tables = htmlParse.find_all("table")
        try: t = pd.read_html(tables[0].prettify())[0]
        except:
            _log.warning(f"parsing of {version_time} failed")
        # add date
        t.columns = ["region", "tests"]
        try: t.tests = pd.to_numeric(t.tests.str.replace(" ",""))
        except: pass
        t.insert(0, "date", [version_time for _ in range(t.shape[0])])
        t.region.replace({'łącznie': None}, inplace = True)
        def lookup_region(r):
            try: return _nuts2_pl[r]
            except: return None
        t['nuts'] = t.region.apply(lookup_region)
        x = x.append(t, ignore_index=True)
            
    return x

import logging
_log = logging.getLogger(__name__)

__all__ = ["deaths","covid_death_cases","covid_deaths","covid_tests_wayback"]

