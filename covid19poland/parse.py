
import warnings

from bs4 import BeautifulSoup
import pandas as pd

from . import wiki


def get(level = 1, dt = None):
    x = wiki.get_wiki(level = level, dt = dt)
    # ...
    return x

__all__ = ["get"]