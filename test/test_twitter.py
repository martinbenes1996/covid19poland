
from datetime import datetime
import unittest

import covid19poland as PL


class TestTwitter(unittest.TestCase):
    def test_twitter_output(self):
        results = PL.twitter(start = datetime(2020,6,10), end = datetime(2020,6,11))
        # type of result
        self.assertIsInstance(results, tuple)
        self.assertEqual(len(results), 3)
        self.assertIsInstance(results[0], dict)
        self.assertIsInstance(results[1], dict)
        self.assertIsInstance(results[2], list)
        
        for date,data in results[0].items():
            # key format
            self.assertIsInstance(date, str)
            raised = False
            try: datetime.strptime(date, "%Y-%m-%d")
            except: raised = True
            self.assertTrue(not raised)
            # value format
            self.assertIsInstance(data, dict)
            self.assertEqual(len(data), 1)
            self.assertIn("deaths", data)
            deaths = data['deaths']
            # deaths format
            self.assertIsInstance(deaths, dict)
            self.assertIn("deaths", deaths)
            self.assertIn("people", deaths)
            self.assertIn("url", deaths)
            self.assertIn("parsed", deaths)
            self.assertIn("text", deaths)
            # format requirements
            url = deaths["url"]
            self.assertTrue(isinstance(url, list) and len(deaths["url"]) > 0 and deaths["deaths"] > 0)
            
            
            

__all__ = ["TestTwitter"]