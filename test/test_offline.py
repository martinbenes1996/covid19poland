
from datetime import datetime
import unittest

import pandas as pd

import covid19poland as PL


class TestOffline(unittest.TestCase):
    def test_offline(self):
        result = PL.offline.read()
        # types
        self.assertIsInstance(result, pd.DataFrame)
        for c in ["date","age","gender","place","comorbid","serious","reported"]:
            self.assertIn(c, result.columns)
        # values
        self.assertTrue(all(isinstance(d,datetime) for d in result["date"]))
        self.assertEqual(result["age"].dtypes, float)
        self.assertTrue(all(g in ["M","F",None] for g in result["gender"]))
        self.assertTrue(all(c in [True,False,None] for c in result["comorbid"]))
        self.assertTrue(all(s in [True,False,None] for s in result["serious"]))
        self.assertTrue(all(isinstance(r,datetime) for r in result["reported"]))
        
        
        
            
            
            

__all__ = ["TestOffline"]