
from datetime import datetime,timedelta
import json
import requests

class Fetcher:
    def __init__(self, url, dt):
        self._url = url
        self._dt = dt
    def __call__(self):
        self._response = requests.get(self._url)
        return self._response
    def __enter__(self):
        try:
            return self._response
        except:
            return self()
    def __exit__(self, type, value, traceback):
        print("Type:", type)
        print("Value:", value)
        print("Traceback:", traceback)
    # getters
    def url(self): return self._url
    def date(self): return self._dt
    
class WaybackMachineError(Exception):
    def __init__(self, msg):
        self._msg = msg
    def __str__(self):
        return self._msg

# 'https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Poland'
class WaybackMachine:
    def __init__(self, url='https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2'):
        self._url = url
        self._now = datetime.now()
    def __iter__(self):
        # yield real url
        with Fetcher(self._url, self._now) as response:
            yield response
        # yield date sequence from archive
        dt = self._now
        versions = set()
        while dt > datetime(2020,3,1):
            dt -= timedelta(hours = 12)
            # get older version
            archive_url = self._construct_archive_url(dt)
            url,url_dt = self._fetch_archive(archive_url)
            print(dt, url_dt)
            if url_dt not in versions:
                versions.add(url_dt)
                with Fetcher(url, url_dt) as response:
                    yield response
            if url_dt < dt:
                dt = url_dt
            
    def _construct_archive_url(self, dt = None):
        archive_url = f"http://archive.org/wayback/available?url={self._url}"
        if dt is not None:
            archive_url += f"&timestamp={ dt.strftime('%Y%m%d') }"
        return archive_url
    def _fetch_archive(self, archive_url):
        # fetch
        try:
            response = requests.get(archive_url)
        except:
            raise WaybackMachineError("failed connecting to archive")
        try:
            x = json.loads(response.text)['archived_snapshots']['closest']
            # parse
            return x['url'],datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S")
        except:
            raise WaybackMachineError("error parsing archive response")

__all__ = ["Fetcher","WaybackMachine"]