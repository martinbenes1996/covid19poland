

from datetime import datetime,date,timedelta
import json
import re
import time
import warnings

from bs4 import BeautifulSoup
import pandas as pd
import requests

from .PLtwitter import *

def create_url(dt = None):
    if dt is not None:
        # date,datetime OK
        if isinstance(dt, date) or isinstance(dt, datetime): pass
        # parse string date
        elif isinstance(dt, str):
            try: dt = datetime.strptime("%Y-%m-%d")
            except: 
                try: dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                except:
                    try: dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
                    except: raise ValueError("unknown format of date")
        # unsupported date type
        else: raise TypeError("unknown type of date")
    # create url
    urlparam = 'url=https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Poland'
    dtparam = f"&timestamp={ dt.strftime('%Y%m%d') }" if dt is not None else ""
    return f'http://archive.org/wayback/available?{urlparam}{dtparam}'
    
def fetch_www_json(url, dt = None):
    if dt is None:
        return 'https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Poland',datetime.now()
    # receive www json
    body = json.loads(requests.get(url).text)
    # parse
    source_url = body['archived_snapshots']['closest']['url']
    source_dt = body['archived_snapshots']['closest']['timestamp']
    return source_url,datetime.strptime(source_dt, "%Y%m%d%H%M%S")

def get_previous_dt(dt = None):
    if dt is None:
        dt = datetime.now()
    # recursion condition
    if dt < datetime(2020,4,30):
        raise Exception("no earlier page found")
    # get closest date
    url = create_url(dt)
    url_w,dt_w = fetch_www_json(url)
    # changed
    if dt > dt_w:
        return dt_w
    else:
        get_previous_dt(dt - timedelta(days=1))

def parse_poland(x):
    # get table
    t = pd.read_html(x[0].prettify())[0]
    # format table
    t.columns = ["date","suspected","quarantined","monitored","tested","confirmed_daily","confirmed","active","recovered","deaths_official","deaths_unofficial","source"]
    t = t[:-3].fillna(0).drop("source", axis=1)
    t["date"] = t["date"].apply(lambda s: datetime.strptime(re.search("^[0-9]+ [a-zA-Z]+ [0-9]+",s).group(0), '%d %B %Y'))
    for col in ["suspected","quarantined","monitored","tested","confirmed_daily","confirmed","active","recovered","deaths_official","deaths_unofficial"]:
        t[col] = t[col].apply(lambda s: int(re.search("^-?[0-9]+",str(s)).group(0)))
        
    return t

states = ["DS","KP","LB","LD","LU","MA","MZ","OP","PD","PK","PM","SK","SL","WN","WP","ZP"]
def parse_states(x):
    # get tables
    t_confirmed = pd.read_html(x[1].prettify())[0]
    t_deaths = pd.read_html(x[2].prettify())[0]
    # format tables
    t_deaths.columns = t_confirmed.columns = ["date",*states,"daily","total","source"]
    t_confirmed = t_confirmed[:-3].fillna(0).drop(["daily","total","source"], axis=1)
    t_deaths = t_deaths[:-3].fillna(0).drop(["daily","total","source"], axis=1)
    # parse tables
    parse_date = lambda dt: datetime.strptime(re.search("^[0-9]+ [a-zA-Z]+ [0-9]+", dt).group(0), '%d %B %Y')
    t_confirmed["date"] = t_confirmed["date"].apply(parse_date)
    t_deaths["date"] = t_deaths["date"].apply(parse_date)
    # parse numbers
    parse_int_prefix = lambda i: int(re.search("^-?[0-9]+", str(i)).group(0))
    for col in states:
        t_confirmed[col] = t_confirmed[col].apply(parse_int_prefix)
        t_deaths[col] = t_deaths[col].apply(parse_int_prefix)
    # wide to long
    confirmed = t_confirmed.melt(id_vars='date', value_vars=states, var_name="state", value_name="confirmed")
    deaths = t_deaths.melt(id_vars='date', value_vars=states, var_name="state", value_name="deaths")
    # join
    xx = confirmed.merge(deaths, on=["date","state"], how="outer")
    xx["confirmed"] = xx["confirmed"].fillna(0).apply(parse_int_prefix)
    xx["deaths"] = xx["deaths"].fillna(0).apply(parse_int_prefix)
    
    return xx

def fetch_table(table_parser = lambda x: _, dt = None):
    # create archive url
    archive_url = create_url(dt)
    # fetch json
    try:
        url,dt = fetch_www_json(archive_url)
    except:
        print("error accessing archive")
        raise
    # fetch wiki
    time.sleep(1)
    try:
        response = requests.get(url)
    except:
        print("error accessing page")
        raise
    # parse
    try:
        wiki = BeautifulSoup(response.text, features="lxml")
        tables = wiki.find_all("table", class_="wikitable")
        t = table_parser(tables)
    # error
    except:
        pass
    # ok
    else:
        return t

    # on error, fetch from archiveanother page
    try:
        dt_prev = get_previous_dt(dt)
    except:
        print("error fetching previous date")
        raise
 
    try:
        t = fetch_table(table_parser, dt_prev)
    except:
        print("error fetching table")
    return t

def fetch1(dt = None):
    return fetch_table(parse_poland, dt)
def fetch2(dt = None):
    return fetch_table(parse_states, dt)

def twitter(start = None, end = None):
    data,ignored,checkdates = PolishTwitter.get(end = end, start = start, keys = ['deaths'])
    if checkdates:
        print(checkdates)
        return data,ignored,checkdates
    else:
        return data,ignored,checkdates

def fetch(level = 1, dt = None):
    if level == 1:
        return fetch_table(parse_poland, dt)
    elif level == 2:
        return fetch_table(parse_states, dt)
    else:
        warnings.warn("unsupported level")
        return None
    
__all__ = ["fetch","twitter"]

if __name__ == "__main__":
    raise NotImplementedError
