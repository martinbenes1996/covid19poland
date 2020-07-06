
from datetime import datetime
import unittest

import pandas as pd

import covid19poland as PL


class TestWiki(unittest.TestCase):
    def test_wiki(self):
        x = PL.wiki(dt = "2020-06-08")
        # type
        self.assertIsInstance(x, pd.DataFrame)
        data_columns = ["suspected","quarantined","monitored","tested","confirmed_daily",
                        "confirmed","active","recovered","deaths_official","deaths_unofficial"]
        for c in ["date", *data_columns]:
            self.assertIn(c, x.columns)
        # values
        self.assertTrue(all(isinstance(d, datetime) for d in x.date))
        for i in data_columns:
            self.assertTrue(all(isinstance(j, int) for j in x[i]))
        # check nondescending (some)

__all__ = ["TestWiki"]