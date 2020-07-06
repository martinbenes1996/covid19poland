
from datetime import datetime
from io import BytesIO
import json
import pkg_resources

import pandas as pd
import requests

class PlaceParser:
    _url = 'https://ec.europa.eu/eurostat/documents/345175/501971/EU-28-LAU-2019-NUTS-2016.xlsx'
    _filename = pkg_resources.resource_filename(__name__, "data/NUTS_PL.csv")
    _loaded = False
    _x = None
    
    @classmethod
    def _load(cls):
        if not cls._loaded:
            cls._x = pd.read_csv(cls._filename)
            cls._loaded = True
    @classmethod
    def parse(cls, city):
        cls._load()
        line = cls._x[cls._x["LAU NAME NATIONAL"] == city]
        nuts3 = line.reset_index(drop = True).at[0, 'NUTS 3 CODE']
        return nuts3[:-1], nuts3

def _parse_place(place):
    try:
        return PlaceParser.parse(place)
    except:
        return None,None
    
def read():
    
    data = []
    for f in ["2020-03","2020-04","2020-05","2020-06"]:
        filename = pkg_resources.resource_filename(__name__, f'data/{f}.json')
        with open(filename, encoding = "UTF-8") as fd:
            raw = json.load(fd)
            for k,v in raw.items():
                dt = datetime.strptime(k, "%Y-%m-%d")
                deaths = v["deaths"]
                
                if "people" in deaths:
                    for death in deaths["people"]:
                        # place
                        place = death.get("place", None)
                        nuts2, nuts3 = _parse_place(place)
                        # reported
                        try: reported = datetime.strptime(death["time"], "%Y-%m-%d %H:%M:%S")
                        except: reported = None
                        # gender
                        gender = death.get("gender", None)
                        # age
                        age = death.get("age", None)
                    
                        # flags
                        comorbid = death.get("comorbid", None)
                        serious = death.get("serious", None)
                    
                        data.append([dt, age, gender, place, nuts2, nuts3, comorbid, serious, reported])
    return pd.DataFrame(data, columns = ["date","age","gender","place","NUTS2","NUTS3","comorbid","serious","reported"])

if __name__ == "__main__":
    x = read()
    print(x)
    
__all__ = ["read"]