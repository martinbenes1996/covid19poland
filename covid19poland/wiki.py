
from datetime import datetime
import re
import warnings

from bs4 import BeautifulSoup
import pandas as pd

from . import fetch

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

def get_wiki_tables(table_parser = lambda x: _, dt = None):
    # create archive url
    for response in fetch.WaybackMachine('https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Poland'):
        try:
            wiki = BeautifulSoup(response.text, features="lxml")
            tables = wiki.find_all("table", class_="wikitable")
            t = table_parser(tables)
        except:
            pass
        else:
            break
    return t

def get_wiki(level = 1, dt = None):
    if level == 1:
        return get_wiki_tables(parse_poland, dt)
    elif level == 2:
        return get_wiki_tables(parse_states, dt)
    else:
        warnings.warn("unsupported level")
        return None

__all__ = ["get_wiki"]