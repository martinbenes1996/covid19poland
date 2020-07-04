# -*- coding: utf-8 -*-
"""Webscraper for Poland COVID19 data. Uses archive.org if fails scraping.
 
Sources:
    * https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Poland
    * ...
Todo:
    * More sources
    * Caching
"""

import pkg_resources
from .offline import *
from .main import *
from .parse import *

try:
    __version__ = pkg_resources.get_distribution("covid19poland").version
except:
    __version__ = None