
from datetime import datetime
from io import BytesIO
import json
import pkg_resources
import tempfile

import covid19dh
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
            try:
                cls._x = pd.read_csv(cls._filename)
            except KeyboardInterrupt:
                raise
            except:
                res = requests.get(cls._url)
                with tempfile.TemporaryFile() as fd:
                    fd.write(res.content)
                    fd.seek(0)
                    cls._x = pd.read_excel(fd, sheet_name="PL")
                cls._x.to_csv(cls._filename, index = False)
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
    
def covid_death_cases(source = None):
    if source is None:
        files = [pkg_resources.resource_filename(__name__, f'data/{f}.json')
                 for f in ["2020-03","2020-04","2020-05","2020-06","2020-07"]]
        source = {}
        for filename in files:
            with open(filename, encoding = "UTF-8") as fd:
                raw = json.load(fd)
                source = {**source, **raw}
    
    data = []
    for k,v in source.items():
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
                reliable = deaths.get("parsed", True)
                    
                data.append([dt, age, gender, place, nuts2, nuts3, comorbid, serious, reliable, reported])
    return pd.DataFrame(data, columns = ["date","age","sex","place","NUTS2","NUTS3","comorbid","serious","reliable","reported"])

def mismatching_days():
    # get data
    cases = covid_death_cases()
    x = cases.groupby(["date"]).size().reset_index(name='case_agg')    
    # reference
    ref = covid19dh.covid19("Poland", verbose = False)[["date","deaths"]]
    ref['deaths'] = ref.deaths.diff()
        
    # merge
    x = x.merge(ref, on = "date")
        
    # parse not matching
    x = x[x.case_agg != x.deaths]
    return x

__all__ = ["covid_death_cases","mismatching_days"]