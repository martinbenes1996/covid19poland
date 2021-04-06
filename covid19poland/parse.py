
import datetime
import io
import math
import warnings

from bs4 import BeautifulSoup
import pandas as pd
import requests

from . import export
from . import PLwiki
from . import PLstat
from . import PLtwitter
from . import offline as offline_module

def wiki(level = 1, dt = None):
    x = PLwiki.get_wiki(level = level, dt = dt)
    return x

def twitter(start = None, end = None, keys = ['deaths']):
    """Parses tweets of Polish Ministry of Health and returns numbers.
    
    Args:
        start (datetime,optional): Start date of the tweets to parse (inclusive).
        end (datetime, optional): End date of the tweets to parse (exclusive).
        keys (list, optional): List of string keys listing the output items. Available are
            * daily = daily reports (must be manually parsed)
            * deaths = new death announcements
            * tests = cumulative number of performed tests (in thousands)
            * cases = new confirmed cases
            * cumulative = cumulative number of confirmed cases
            * regions = regional new confirmed cases
    Returns:
        (dict): parsed data with linked sources (tweet URLs)
        (dict): ignored tweets
        (list): dates to check manually (partial errors)
    """
    results = PLtwitter.PolishTwitter.get(start = start, end = end, keys = keys)
    return results

def deaths(offline = True):
    """Returns deaths counts by sex and year in Poland.
    
    Args:
        offline (bool, optional): Use saved csv, defaultly true.
    Returns:
        (pandas.DataFrame): death counts
    """
    result = PLstat.deaths(offline = offline)
    return result

def covid_death_cases(offline = True, from_github = False):
    """Returns covid-19 deaths cases by sex and date in Poland.
    
    Args:
        offline (bool, optional): Use saved csv, defaultly true.
        from_github(bool, optional): Use file from github, defaultly false.
    Returns:
        (pandas.DataFrame): death cases
    """
    result = PLstat.covid_death_cases(offline = offline)
    return result

def covid_deaths(level = 3, offline = True, from_github = False):
    """Returns deaths counts by age group, sex and week in Poland.
    
    Args:
        offline (bool, optional): Use saved csv, defaultly true.
        from_github(bool, optional): Use file from github, defaultly false.
    Returns:
        (pandas.DataFrame): death counts
    """
    result = PLstat.covid_deaths(level = level, offline = offline, from_github = False)
    return result

def covid_tests(level = 1, offline = True, from_github = False):
    # invalid level
    if level not in {1,2}:
        warnings.warn("level must be from {1,2}")
        return None

    # offline data
    if offline:
        if level == 1:
            x = offline_module.covid_tests()
        else:
            raise NotImplementedError("not implemented yet")
            #return offline_module.covid_tests2()
    # from github
    elif from_github:
        # read csv from github
        tests_url = 'https://raw.githubusercontent.com/martinbenes1996/covid19poland/master/data/tests.csv'
        tests_response = requests.get(tests_url)
        # csv to pandas
        x = pd.read_csv( io.StringIO(tests_response.text) )
        x['date'] = x.date.apply(lambda dt: datetime.datetime.strptime(dt, '%Y-%m-%d'))
        x_country,x_region = x[x.region.isna()],x[~x.region.isna() & (x.region != 'PL72')]
        # solve PL72
        x_PL72 = x[(x.region == 'PL72')]
        x_PL72['dtests'] = 0
        x_PL72['dtests'] = x_PL72[x_PL72.date <= datetime.datetime(2020,8,6)]['tests'].diff()\
            .append(x_PL72[x_PL72.date > datetime.datetime(2020,8,6)]['tests'].diff())
        x_PL72['tests'] = x_PL72.apply(lambda r: r.dtests if not math.isnan(r.dtests) else r.tests, axis = 1)\
            .cumsum()
        x_region = x_region\
            .append(x_PL72, ignore_index = True)\
            .sort_values(['date','region'])
        # tests to daily
        x_country.loc[:,'tests'] = x_country['tests'].diff().fillna(0)
        x_region.loc[:,'tests'] = x_region.groupby('region').tests.diff().fillna(0)
        # only weekly
        x_region = x_region[x_region.tests != 0]
        # per country
        if level == 1:
            # aggregate regions
            x = x_region\
                .groupby('date')\
                .aggregate({'tests': 'sum'})\
                .reset_index()
            # merge with country
            duplicated = x[x.date.duplicated()].date
            x['reg'] = True
            x_country['reg'] = False
            x = x\
                .append(x_country[['date','tests','reg']], ignore_index=True)\
                .sort_values('date')
            # deduplicate (prefer country)
            x['dup'] = x.date.isin(x[x.date.duplicated()].date)
            x = x[~x.dup | x.dup & ~x.reg]
            x = x[['date','tests']]
            # fill gaps
            x_add = {'date': []}
            for dt in pd.date_range(x.date.min(), x.date.max()):
                if x[x.date == dt].empty:
                    x_add['date'].append(dt)
        # regional      
        else:    
            x = x_region
            # fill gaps
            x_add = {'date': [], 'region': []}
            for dt in pd.date_range(x.date.min(), x.date.max()):
                for reg in x.region.unique():
                    if x[(x.date == dt) & (x.region == reg)].empty:
                        x_add['date'].append(dt)
                        x_add['region'].append(reg)
        x_add = pd.DataFrame({**x_add, 'tests': 0})
        x = x.append(x_add, ignore_index=True)\
            .sort_values('date')\
            .reset_index(drop = True)   
        x['week'] = x.date.apply( lambda dt: dt.isocalendar()[1] )
        return x
    
    # online data
    else:
        if level == 1:
            data,filtered,checklist = PLtwitter.PolishTwitter.get(
                start=datetime.datetime(2020,3,15),
                keys=["tests"])
            x = offline_module.covid_tests(source = data)
        else:
            x = PLstat.covid_tests_wayback(end = datetime.datetime(2020,5,12))
            x = x[~x.region.isnull()]
    # reset index and return
    return x.reset_index(drop = True)

def mismatching_days():
    """Returns dates not matching the `covid19dh` data."""
    return offline_module.mismatching_days()

def export_month(dt = None, offset = -1):
    # set logging
    import logging
    logging.basicConfig(level = logging.INFO)
    # relative date
    now = dt if dt is not None else datetime.datetime.now()
    # construct input
    fname = f"{now.month + offset}"
    start = datetime.datetime(now.year, now.month + offset, 1)
    end = datetime.datetime(now.year, now.month + offset + 1, 1)
    # export
    export.export(start = start, end = end, fname = fname)
def export_manual():
    # set logging
    import logging
    logging.basicConfig(level = logging.INFO)
    # get data
    x = covid_death_cases(offline = True)
    # export
    x.to_csv("data/data.csv", index = False)
def export_last_30d():
    # set logging
    import logging
    logging.basicConfig(level = logging.INFO)
    # relative date
    now = datetime.datetime.now()
    # construct input
    fname = f"last30d"
    start = datetime.datetime(now.year, now.month, now.day) - datetime.timedelta(days=30)
    end = datetime.datetime(now.year,now.month,now.day) + datetime.timedelta(days=1)
    # export
    export.export_csv(start = start, end = end, fname = fname)
def export_tests():
    # set logging
    import logging
    logging.basicConfig(level = logging.INFO)
    # construct input
    export.export_test_csv(append = True)
    
__all__ = [
    "wiki", "twitter", "deaths", "covid_death_cases", "covid_deaths", "covid_tests",
    "mismatching_days",
    "export_month", "export_manual", "export_last_30d", "export_tests"
]