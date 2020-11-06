

import unittest

import pandas as pd

import covid19poland as PL


class TestStat(unittest.TestCase):
    def get_deaths(self, *args, **kw):
        x = PL.deaths(*args, **kw)
        
        self.assertIsInstance(x, pd.DataFrame)
        self.assertIn("Year", x.columns)
        self.assertIn("Sex", x.columns)
        self.assertIn("Total", x.columns)
        for y in range(1, 13):
            self.assertIn(str(y), x.columns)
        
        return x
    def get_covid_death_cases(self, *args, **kw):
        x = PL.covid_death_cases(*args, **kw)
        
        self.assertIsInstance(x, pd.DataFrame)
        self.assertIn("date", x.columns)
        self.assertIn("age", x.columns)
        self.assertIn("sex", x.columns)
        self.assertIn("place", x.columns)
        self.assertIn("NUTS2", x.columns)
        self.assertIn("NUTS3", x.columns)
        self.assertIn("comorbid", x.columns)
        self.assertIn("serious", x.columns)
        self.assertIn("comorbid", x.columns)
        
        return x
    def get_covid_deaths(self, *args, **kw):
        x = PL.covid_deaths(*args, **kw)
        
        self.assertIsInstance(x, pd.DataFrame)
        self.assertIn("week", x.columns)
        self.assertIn("sex", x.columns)
        self.assertIn("age_group", x.columns)
        self.assertIn("deaths", x.columns)
        
        return x
    
    def test_deaths_offline(self):
        x = self.get_deaths()
    def test_deaths_online(self):
        x = self.get_deaths(offline = False)
    
    def test_death_cases_offline(self):
        x = self.get_covid_death_cases()
    #def test_death_cases_online(self):
    #    x = self.get_covid_death_cases(offline = False)
    
    def test_covid_deaths3_offline(self):
        x = self.get_covid_deaths(level = 3, offline = True)
        print("test_covid_deaths3_offline", x.columns)
        self.assertIn("NUTS2", x.columns)
        self.assertIn("NUTS3", x.columns)
    #def test_covid_deaths3_online(self):
    #    x = self.get_covid_deaths(level = 3, offline = False)
    def test_covid_deaths2_offline(self):
        x = self.get_covid_deaths(level = 2, offline = True)
        print("test_covid_deaths2_offline", x.columns)
        self.assertIn("NUTS2", x.columns)
    #def test_covid_deaths2_online(self):
    #    x = self.get_covid_deaths(level = 2, offline = False)
    def test_covid_deaths1_offline(self):
        x = self.get_covid_deaths(level = 1, offline = True)
    #def test_covid_deaths1_online(self):
    #    x = self.get_covid_deaths(level = 1, offline = False)
        
__all__ = ["TestStat"]