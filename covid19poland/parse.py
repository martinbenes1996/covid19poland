
import warnings

from bs4 import BeautifulSoup
import pandas as pd

from . import PLwiki
from . import PLstat
from . import PLtwitter


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
    """Returns deaths by sex and month in Poland.
    
    Args:
        offline (bool, optional): Use saved csv, defaultly true.
    Returns:
        (pandas.DataFrame): death counts
    """
    result = PLstat.deaths(offline = offline)
    return result

__all__ = ["wiki", "twitter", "deaths"]