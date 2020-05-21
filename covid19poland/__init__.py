# -*- coding: utf-8 -*-
"""Webscraper for Wikipedia. Uses archive.org if fails scraping.
 
Reference: https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Poland
Todo:
    * caching
"""

import pkg_resources
from .main import *

try:
    __version__ = pkg_resources.get_distribution("covid19_PL_wiki").version
except:
    __version__ = None