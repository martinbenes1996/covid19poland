
from datetime import datetime
import json
from pathlib import Path

import pandas as pd

def _parse_place(place):
    return place

def read():
    
    data = []
    for f in ["2020-03","2020-04","2020-05","2020-06"]:
        with open(Path("data") / f"{f}.json", encoding = "UTF-8") as fd:
            raw = json.load(fd)
            for k,v in raw.items():
                dt = datetime.strptime(k, "%Y-%m-%d")
                deaths = v["deaths"]
                
                if "people" in deaths:
                    for death in deaths["people"]:
                        # place
                        place = death.get("place", None)
                        place = _parse_place(place)
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
                    
                        data.append([dt, age, gender, place, comorbid, serious, reported])
    return pd.DataFrame(data, columns = ["date","age","gender","place","comorbid","serious","reported"])

if __name__ == "__main__":
    x = read()
    print(x)

__all__ = ["read"]