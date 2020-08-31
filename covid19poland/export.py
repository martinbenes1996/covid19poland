# global imports
import json
import warnings
# local imports
from .PLtwitter import *

def export(start, end, fname, keys = ["deaths"]):
    data,filtered,checklist = PolishTwitter.get(start, end, keys=keys)
    with open(f"data/{fname}_in.json", "w") as fd:
        json.dump(data, fd, sort_keys=True, indent = 4, separators = (',',": "))
    with open(f"data/{fname}_out.json", "w") as fd:
        json.dump(filtered, fd, sort_keys=True, indent = 4, separators = (',',": "))
    if checklist:
        warnings.warn(f"failed to parse {len(checklist)} days")
    

# logging
if __name__ == "__main__":
    import logging
    logging.basicConfig(level = logging.INFO)

__all__ = ["export"]
if __name__ == "__main__":
    export()