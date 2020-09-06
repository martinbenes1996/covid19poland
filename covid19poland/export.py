# global imports
import datetime
import io
import json
import pandas as pd
import warnings
# local imports
from .PLtwitter import *
from . import offline
from . import PLstat

def export(start, end, fname, keys = ["deaths"]):
    data,filtered,checklist = PolishTwitter.get(start, end, keys=keys)
    with open(f"data/{fname}_in.json", "w") as fd:
        json.dump(data, fd, sort_keys=True, indent = 4, separators = (',',": "))
    with open(f"data/{fname}_out.json", "w") as fd:
        json.dump(filtered, fd, sort_keys=True, indent = 4, separators = (',',": "))
    if checklist:
        warnings.warn(f"failed to parse {len(checklist)} days")
    
def export_csv(start, end, fname, keys = ["deaths"]):
    data,filtered,checklist = PolishTwitter.get(start, end, keys=keys)
    with open(f"data/{fname}_in.json", "w") as fd:
        json.dump(data, fd, sort_keys=True, indent = 4, separators = (',',": "))
    x = offline.covid_death_cases(data)
    x.to_csv(f"data/{fname}.csv", index = False)
    if checklist:
        warnings.warn(f"failed to parse {len(checklist)} days")

def export_test_csv(start = None, end = None, append = False, fname = "tests"):
    # download
    x1 = offline.covid_tests() # L1
    x2 = PLstat.covid_tests_wayback(start = start, end = end) # L2
    # merge
    x = pd.DataFrame({'date': x1.date, 'region': None, 'tests': x1.tests_all})
    x2 = pd.DataFrame({'date': x2.date, 'region': x2.nuts, 'tests': x2.tests})
    x2 = x2[~x2.region.isnull()]
    x = x.append(x2)
    def _parse_date(dt):
        try: return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
        except: pass
        try: return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except: pass
        try: return datetime.datetime.strptime(dt, "%Y-%m-%d")
        except: pass
        return dt
    # sort
    x['date'] = x.date.apply(_parse_date)
    x = x.sort_values(["date","region"])
    # append (if set on)
    if append:
        # read previous data
        try:
            x_ex = pd.read_csv(f"data/{fname}.csv")
            x_ex['date'] = x_ex.date.apply(_parse_date)
            # append
            x = x_ex.append(x).sort_values(["date"], kind = 'mergesort')
        except: pass
    # if missing, warn
    if x.tests.isna().any():
        warnings.warn("NaN tests produced")
    # export
    x.date = x.date.apply(lambda dt: dt.strftime("%Y-%m-%d"))
    x = x.drop_duplicates(["date","region"], keep = 'last')
    x.to_csv(f"data/{fname}.csv", index = False)
    
        
# logging
if __name__ == "__main__":
    import logging
    logging.basicConfig(level = logging.INFO)

__all__ = ["export", "export_csv", "export_test_csv"]

if __name__ == "__main__":
    export()