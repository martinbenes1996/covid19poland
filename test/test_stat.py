

import unittest

import pandas as pd

import covid19poland as PL


class TestStat(unittest.TestCase):
    def get_deaths(self, *args, **kwargs):
        x = PL.deaths(*args, **kwargs)
        
        self.assertIsInstance(x, pd.DataFrame)
        self.assertIn("Year", x.columns)
        self.assertIn("Sex", x.columns)
        self.assertIn("Total", x.columns)
        for y in range(1, 13):
            self.assertIn(str(y), x.columns)
        
        return x
    
    def test_deaths_offline(self):
        x = self.get_deaths()
    def test_deaths_online(self):
        x = self.get_deaths(offline = False)   
        
__all__ = ["TestStat"]