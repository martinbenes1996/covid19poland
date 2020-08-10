
from datetime import datetime,timedelta
from functools import reduce
import json
import logging
import re
import warnings

import GetOldTweets3 as got3

class FlaggedTweet:
    def __init__(self, tweet, relevant = True, deaths = False, cases = False, tests = False, regions = False, daily = False, cumulative = False, partial = False):
        self.tweet = tweet
        self.associated = None
        self.flags = {
            "relevant": relevant,
            "deaths": deaths,
            "cases": cases,
            "tests": tests,
            "regions": regions,
            "daily": daily,
            "cumulative": cumulative,
            "partial": partial }
    def __repr__(self):
        if self.flags["relevant"]:
            s = f"\033[92m{self.tweet.text}\033[00m\n\t"
            s += f"\tLink: {self.tweet.permalink}\t"
            for key in self.flags:
                if self.flags[key] is True:
                    s += f"\033[1m#{key}\033[00m "
            return s
        else:
            s = f"\033[91m{self.tweet.text}\033[00m\n"
            s += f"\nLink: {self.tweet.permalink}"
            return s

class PolishTwitter:
    wojewodstwa_keywords = {
        r"(?<!dolno)śląski[\w]*": "PL22", r"mazowiecki[\w]*": "PL92", r"łódzki[\w]*": "PL71", r"dolnośląski[\w]*": "PL51",
        r"małopolski[\w]*": "PL21", r"podlaski[\w]*": "PL84", r"lubelski[\w]*": "PL81", r"lubuski[\w]*": "PL43",
        r"pomorski[\w]*": "PL63", r"wielkopolski[\w]*": "PL41", r"kujawsko-pomorski[\w]*": "PL61",
        r"zachodniopomorski[\w]*": "PL42", r"świętokrzyski[\w]*": "PL72", r"(?<!mał)(?<!wielk)opolski[\w]*": "PL52",
        r"warmińsko-mazurski[\w]*": "PL62", r"podkarpacki[\w]*": "PL82"}
    cities_keywords = {
        "Warszaw[\w]*": "PL127",
        "Krak\ww[\w]*": "PL213",
        "Łód[\w]*": "PL711",
        "Radom[\w]*": "PL921",
        "Bytom[\w]*": "PL228",
        "Katowic[\w]*": "PL22A",
        "Tych[\w]*": "PL22C",
        "Wrocław[\w]*": "PL514",
        "Gdańsk[\w]*": "PL634",
        "Racib[\w]*": "PL227",
        "Legnic[\w]*": "PL516",
        "Przemy[\w]*": "PL822",
        "Gliwic[\w]*": "PL229",
        "Zgierz[\w]*": "PL712",
        "Kędzierzyn[\w]*": "PL524",
        "Zawierc[\w]*": "PL22B",
        "Cieszy[\w]*": "PL311",
        "Bielsk[\w]*": "PL311",
        "Pozna[\w]*": "PL415",
        "Bolesław[\w]*": "PL515",
        "Starachowic[\w]*": "PL721",
        "Łańcu[\w]*": "PL823",
        "Kozienic[\w]*": "PL921",
        "Koszalin[\w]*": "PL426",
        "Limanow[\w]*": "PL218",
        "Pleszew[\w]*": "PL416",
        "Lub(lin|el)[\w]*": "PL814",
        "Grudziąd[\w]*": "PL616",
        "Ostr[óo]d[\w]*": "PL621",
        "Puław[\w]*": "PL112",
        "Wysok[\w]*": "PL344",
        "Jarosław[\w]*": "PL822",
        "Oleśnic[\w]*": "PL722",
        "Ozim[\w]*": "PL524"
    }
    @staticmethod
    def _daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)
    def __init__(self, start = None, end = None):
        self._log = logging.getLogger(self.__class__.__name__)
        self._username = "MZ_GOV_PL"
        self._start = start if start else datetime(2020,6,1)
        self._end = end if end else datetime.now()
        self._base_criteria = got3.manager.TweetCriteria()\
            .setUsername(self._username)
            #.setMaxTweets(100)
    def __iter__(self):
        for dt in self._daterange(self._start, self._end):
            criteria = self._base_criteria\
                .setSince(dt.strftime("%Y-%m-%d"))\
                .setUntil((dt + timedelta(1)).strftime("%Y-%m-%d"))
            tweets = got3.manager.TweetManager.getTweets(criteria)
            tweets = sorted([tweet for tweet in tweets], key = lambda i: i.date)
            for tweet in tweets:
                yield tweet
    
    def parseAll(self):
        keywords = {"dzienny raport", "mamy [0-9]+", "z przykrością", "ze szpitala",
                    "kobieta", "mężczyzna", "liczba", "W ciągu doby wykonano",
                    "(?<![0-9])([0-9]+)-([KM])(?!etr)( [^,.]*)?"} | set(self.wojewodstwa_keywords.keys())
        for i,tweet in enumerate(self):
            for kw in keywords:
                if re.match(f".*{kw}.*", tweet.text.strip(), re.IGNORECASE):
                    ftweet = self._classify_tweet(tweet)
                    yield ftweet
                    break
            else:
                yield FlaggedTweet(tweet, relevant = False)

    def _classify_tweet(self, tweet):
        ftweet = FlaggedTweet(tweet)
        # daily report = rewrite manually from image
        if re.match(r".*dzienny raport.*", tweet.text, re.IGNORECASE):
            ftweet.flags["daily"] = True
            
        # death numbers
        if any( re.match(f".*{kw}.*", tweet.text, re.IGNORECASE) for kw in ["z przykrością", "ze szpitala", "kobiet", "mężczyz", "(?<![0-9])([0-9]+)-([KM])( [^,.]*)?"]):
            ftweet.flags["deaths"] = True
            
        # test numbers
        if re.match(r".*w ciągu doby wykonano.*", tweet.text, re.IGNORECASE):
            ftweet.flags["tests"] = True
        
        # case numbers
        if re.match(r".*mamy [0-9]+ now[a-z]*.*", tweet.text, re.IGNORECASE):
            ftweet.flags["cases"] = True
        
        # cumulative cases
        if re.match(r".*liczba zakażonych koronawirusem.*", tweet.text, re.IGNORECASE):
            ftweet.flags["cumulative"] = True
            
        # regional data
        contains_region_name = any(re.match(f".*{wojewodstwo}.*", tweet.text, re.IGNORECASE) for wojewodstwo in self.wojewodstwa_keywords)
        if any(re.match(f".*{kw}.*", tweet.text, re.IGNORECASE) for kw in ["koronawirus z województw", "woj\."]) or contains_region_name:
            ftweet.flags["regions"] = True
                    
        if re.match(r".*,$", tweet.text.strip(), re.IGNORECASE):
            ftweet.flags["partial"] = True
                     
        return ftweet
    
    def parseDaily(self, tweet):
        if not isinstance(tweet, list):
            tweet = [tweet]
        l = []
        for t in tweet:
            d = {"text": t.tweet.text, "url": t.tweet.permalink, "parsed": False}
            if re.match(r".*dzienny.*raport.*#koronawirus", t.tweet.text, re.IGNORECASE):
                d['parsed'] = True
            l.append(d)
        return l
    def parseDeaths(self, tweet):
        if not isinstance(tweet, list):
            tweet = [tweet]
        l = []
        for t in tweet:
            d = {"text": t.tweet.text, "url": t.tweet.permalink, "deaths": None, "people": [], "parsed": False}
            if re.match(".*z przykrością.*", t.tweet.text, re.IGNORECASE):
                # parse sentence out
                txt = re.search(r".*(z przykrością.*)", t.tweet.text, re.IGNORECASE).group(1)
                liczba = re.search(r"(.*)Liczba.*", txt, re.IGNORECASE)
                txt = liczba.group(1) if liczba else txt
                
                if re.match(r".*o śmierci [0-9]+(?![0-9]).*", t.tweet.text, re.IGNORECASE):
                    try:
                        deaths = re.search(".*o śmierci ([0-9]+)(?![0-9]).*osób", t.tweet.text, re.IGNORECASE).group(1)
                        d["deaths"] = int(deaths)
                        d["parsed"] = True
                    except:
                        pass
                    
            if not d["parsed"]:
                for pl,no in {"dwóch": 2, "trzech": 3, "czterech": 4, "pięciu": 5, "sześciu": 6, "siedmiu": 7, "ośmiu": 8,
                              "dziewięciu": 9, "dziesięciu": 10, "jedenastu": 11, "dwunastu": 12, "trzynastu": 13, "czternastu": 14,
                              "piętnastu": 15, "szesnastu": 16, "siedemnastu": 17, "osiemnastu": 18, "dziewiętnastu": 19, "dwudziestu": 20}.items():
                    if re.match(f".*śmierci.*{pl}.*osób.*", t.tweet.text, re.IGNORECASE):
                        d["deaths"] = no
                        d["parsed"] = True
                        break
                        
            #if not d["parsed"]: 
            #    try:
            #        ages = re.findall(r"[0-9]+(?=- ?let)", t.tweet.text, re.IGNORECASE)
            #        if ages:
            #            d["number"] = len(ages)
            #            d["parsed"] = True
            #    except: pass
                    
            if not d["parsed"]:
                if re.match(r".*o śmierci[^.]*osoby.*", t.tweet.text, re.IGNORECASE):
                    d["deaths"] = 1
                    d["parsed"] = True
                elif re.match(r".*zmarła[^.]* osoba.*", t.tweet.text, re.IGNORECASE):
                    d["deaths"] = 1
                    d["parsed"] = True
            
            people_match = re.findall(r"(?<![0-9])([0-9]+)-([KM])[^\w,]*(\w+)?", t.tweet.text, re.IGNORECASE)
            if people_match:
                for person_match in people_match:
                    person_match = [p.strip() for p in person_match]
                    
                    person = {"age": None, "gender": None, "place": None}
                    try:
                        person["age"] = int(person_match[0])
                    except:
                        pass
                    try:
                        person["gender"] = {"K":"F", "M":"M"}[person_match[1].upper()]
                    except:
                        pass
                    person["place"] = person_match[2] if person_match[2] else None
                    if person["place"] == "i":
                        person["place"] = None
                    d["people"].append(person)
                
                if d['deaths'] is not None and len(d['people']) != d['deaths']:
                    d['parsed'] = False
            people_match2 = re.findall(r"(?<![0-9])([0-9]+)[^\w0-9]*let[\w]+ (k|m)\w+( (ze szpitala|hospitalizowan[\w]+|w szpitalu) w (\w+))?", t.tweet.text, re.IGNORECASE)
            if people_match2:
                #print("Match2")
                #print(people_match2)
                for person_match in people_match2:
                    person_match = [p.strip() for p in person_match]
                    
                    person = {"age": None, "gender": None, "place": None}
                    try:
                        person['age'] = int(person_match[0])
                    except: pass
                    try:
                        person["gender"] = {"K":"F", "M":"M"}[person_match[1].upper()]
                    except: pass
                    person['place'] = person_match[4] if person_match[4] else None
                    d["people"].append(person)
            
            if d['deaths'] is not None and len(d['people']) != d['deaths']:
                d['parsed'] = False
            
            # naive nuts encoder
            #for i,person in enumerate(d['people']):
            #    if person['place'] is None:
            #        continue
            #    for city,nuts in self.cities_keywords.items():
            #        city_match = re.search(f".*{city}.*", person['place'], re.IGNORECASE)
            #        if city_match:
            #            d['people'][i]['place'] = nuts
            #            break
            #    else:
            #        print(f"{person['place']} not matched")
                
            l.append(d)
        # merge
        if len(l) > 1:
            people = [p for i in l for p in i['people']]
            number = sum(i['deaths'] for i in l if i['deaths'])
            url = [i['url'] for i in l]
            l = {"deaths": number, "people": people, "url": url}
            l['parsed'] = len(people) == number
            l['text'] = None
            if l['parsed']:
                l['ok'] = True
                #print("Merge successful!")
            else:
                l['ok'] = True
                #print("Check merge!")
        elif len(l) == 1:
            l = l[0]
            l['ok'] = True
            #print("Single record!")
            
        return l
            
    def parseRegions(self, tweet):
        if not isinstance(tweet, list):
            tweet = [tweet]
        l = []
        for t in tweet:
            d = {"text": t.tweet.text, "url": t.tweet.permalink, "regions": {}, "regions_regex": {}, "parsed": False}
            
            for region,nuts3 in self.wojewodstwa_keywords.items():
                region_match1 = re.search(f".*([0-9]+) os[a-zó]+ z (woj. |){region}.*", t.tweet.text, re.IGNORECASE)
                region_match2 = re.search(f".*{region} \(([0-9]+)\).*", t.tweet.text, re.IGNORECASE)
                if region_match1:
                    d['regions'][nuts3] = d['regions_regex'][region] = int(region_match1.group(1))
                    d['parsed'] = True
                elif region_match2:
                    i = int(region_match2.group(1))
                    d['regions'][nuts3] = d['regions_regex'][region] = int(region_match2.group(1))
                    d['parsed'] = True
                elif re.match(f".*{region}.*", t.tweet.text, re.IGNORECASE):
                    d['regions'][nuts3] = d['regions_regex'][region] = None
                
            l.append(d)
        return l
    def parseTests(self, tweet):
        if not isinstance(tweet, list):
            tweet = [tweet]
        l = []
        for t in tweet:
            d = {"text": t.tweet.text, "url": t.tweet.permalink, "tests": None, "parsed": False}
            if re.match(".*wykonano.*[0-9,]+ tys\.", t.tweet.text, re.IGNORECASE):
                try:
                    no = re.search("([0-9]+(,[0-9]+)?) tys", t.tweet.text, re.IGNORECASE).group(1,2)
                    d['tests'] = float(no[0].replace(',','.')) * 1000
                    d['parsed'] = True
                except:
                    pass
            l.append(d)
        return l
    def parseCases(self, tweet):
        if not isinstance(tweet, list):
            tweet = [tweet]
        l = []
        for t in tweet:
            d = {"text": t.tweet.text, "url": t.tweet.permalink, "cases": None, "parsed": False}
            if re.match(".*mamy.*nowy.*przypadek.*", t.tweet.text, re.IGNORECASE):
                d["cases"] = 1
                d["parsed"] = True
            if re.match(".*mamy.*[0-9]+.*now.*przypad.*", t.tweet.text, re.IGNORECASE):
                d["cases"] = int(re.search(".*mamy[^0-9]*([0-9]+)[^0-9]*now.*przypad.*", t.tweet.text, re.IGNORECASE).group(1))
                d["parsed"] = True
            l.append(d)     
        return l
    def parseCumulative(self, tweet):
        if not isinstance(tweet, list):
            tweet = [tweet]
        l = []
        for t in tweet:
            d = {"text": t.tweet.text, "url": t.tweet.permalink, "confirmed": None, "deaths": None, "parsed": False}
            if re.match(r".*[0-9 ]+/[0-9 ]+.*", t.tweet.text, re.IGNORECASE):
                s = re.search(r"[^\(]([0-9 ]+)/([0-9 ]+)[^\)]", t.tweet.text, re.IGNORECASE).group(1,2)
                
                d['confirmed'] = int(s[0].replace(' ', ''))
                d['deaths'] = int(s[1].replace(' ', ''))
                d['parsed'] = True
            l.append(d)     
        return l
    
    def parseDay(self, dt, day, keys):
        parsers = {
            'daily': self.parseDaily,
            'deaths': self.parseDeaths,
            'regions': self.parseRegions,
            'tests': self.parseTests,
            'cases': self.parseCases,
            'cumulative': self.parseCumulative
        }
        
        self._log.info(f"parsing tweets from {dt}")
        d,ignored = {},{}
        for key in keys:
            reports = [tweet for tweet in day if tweet.flags[key]]
            try:
                d[key] = parsers[key](reports)
            except:
                warnings.warn(f"parser for {key} not found")
            
        # ignored
        available_parsers = set(parsers.keys())
        ignored['all'] = [tweet for tweet in day if all(not tweet.flags[key] for key in keys)]
        ignored['relevant'] = [{"text": t.tweet.text, "url": t.tweet.permalink, "parsed": False} for t in ignored['all'] if t.flags['relevant']]
        ignored['irrelevant'] = [{"text": t.tweet.text, "url": t.tweet.permalink, "parsed": False} for t in ignored['all'] if not t.flags['relevant']]
        del ignored['all']
        
        return d,ignored
    
    @classmethod
    def get(cls, start = None, end = None, keys = ['deaths']):
        # instantiate Twitter object
        PLTwitter = cls(start, end)
        # initialize variable
        daytweets,currday = [],None
        data,filtered = {},{}
        # iterate tagged tweets
        for t in PLTwitter.parseAll():
            # init current day
            if not currday: currday = t.tweet.date.date()
            # add to day tweets if same date
            if t.tweet.date.date() == currday:
                daytweets.append(t)
            # new day
            else:
                # parse finished day
                daydata,ignored = PLTwitter.parseDay(currday, daytweets, keys)
                data[currday.strftime("%Y-%m-%d")] = daydata
                filtered[currday.strftime("%Y-%m-%d")] = ignored
                # reinitialize
                currday = t.tweet.date.date()
                daytweets = [t]
        
        # collect days to check
        checklist = []
        for dt,record in data.items():
            if 'deaths' in record:
                if isinstance(record['deaths'], list):
                    for i,d in enumerate(record['deaths']):
                        # not okay record
                        if not d['ok']: checklist.append(dt)
                        # remove ok key
                        del data[dt]['deaths'][i]['ok']
                else:
                    # not okay record
                    if not record['deaths']['ok']: checklist.append(dt)
                    # remove ok key
                    del data[dt]['deaths']['ok']
        
        return data,filtered,checklist

__all__ = ["PolishTwitter"]
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    
    data,filtered,checklist = PolishTwitter.get(datetime(2020,7,1),datetime(2020,7,18))

    with open("data/7_in.json", "w") as fd:
        json.dump(data, fd, sort_keys=True, indent = 4, separators = (',',": "))
    with open("data/7_out.json", "w") as fd:
        json.dump(filtered, fd, sort_keys=True, indent = 4, separators = (',',": "))
    print(checklist)

    