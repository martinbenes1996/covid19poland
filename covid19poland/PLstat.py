
import csv
from io import BytesIO
import pkg_resources
from zipfile import ZipFile

import pandas as pd
import requests

def _parse_death_table(df, r = 7):
    df = df.iloc[r,2:].reset_index(drop = True)
    df.columns = ["Total"] + [str(i+1) for i in range(12)]
    return df
def _parse_deaths():
    url = {
        2018: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2018_00_7.zip&sys=zgo',
        2017: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2017_00_7.zip&sys=zgo',
        2016: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2016_00_7.zip&sys=zgo',
        2015: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2015_00_7.zip&sys=zgo',
        2014: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2014_00_7.zip&sys=zgo',
        2013: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2013_00_7.zip&sys=zgo',
        2012: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2012_00_7.zip&sys=zgo',
        2011: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2011_00_7.zip&sys=zgo',
        2010: 'http://demografia.stat.gov.pl/bazademografia/Downloader.aspx?file=pl_zgo_2010_00_7.zip&sys=zgo'
    }
    data = []
    for y in url:
        # download file
        res = requests.get(url[y])
        zip_file = ZipFile(BytesIO(res.content))
        # parse zip
        files = zip_file.namelist()
        tablerow = 9 if y == 2010 else 7
        # parse male data
        with zip_file.open(files[0], 'r') as xlsfile:
            x  = pd.read_excel(xlsfile, sheet_name="MĘŻCZYŹNI")
            xx = [y, "M"] + _parse_death_table(x, tablerow).tolist()
            data.append(xx)
        # parse female data
        with zip_file.open(files[0], 'r') as xlsfile:
            x  = pd.read_excel(xlsfile, sheet_name="KOBIETY")
            xx = [y, "F"] + _parse_death_table(x, tablerow).tolist()
            data.append(xx)
    data = pd.DataFrame(data, columns = ["Year", "Sex", "Total"] + [str(i+1) for i in range(12)])
    data.to_csv(pkg_resources.resource_filename(__name__, "data/deaths.csv"), index = False)
    return data

def deaths(offline = True):
    if offline:
        try:
            return pd.read_csv(pkg_resources.resource_filename(__name__, "data/deaths.csv"))
        except: pass
    return _parse_deaths()
                
    
if __name__ == "__main__":
    x = deaths()
    print(x)

__all__ = ["deaths"]

