
import warnings

from bs4 import BeautifulSoup
import pandas as pd

from . import PLwiki
from . import PLstat
from . import PLtwitter
from . import offline

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

def covid_death_cases(offline = True):
    """Returns covid-19 deaths cases by sex and date in Poland.
    
    Args:
        offline (bool, optional): Use saved csv, defaultly true.
    Returns:
        (pandas.DataFrame): death cases
    """
    result = PLstat.covid_death_cases(offline = offline)
    return result

def covid_deaths(level = 3, offline = True):
    """Returns deaths counts by age group, sex and week in Poland.
    
    Args:
        offline (bool, optional): Use saved csv, defaultly true.
    Returns:
        (pandas.DataFrame): death counts
    """
    result = PLstat.covid_deaths(level = level, offline = offline)
    return result

def mismatching_days():
    """Returns dates not matching the `covid19dh` data."""
    return offline.mismatching_days()

__all__ = [
    "wiki", "twitter", "deaths", "covid_death_cases", "covid_deaths",
    "mismatching_days"
]