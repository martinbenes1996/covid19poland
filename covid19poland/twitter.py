
from datetime import datetime,timedelta
import logging
from functools import reduce
import re

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
class MultiTweet:
    def __init__(self, *args):
        self.tweets = args
        self.text = reduce(lambda a,i: f"{a} {i}", [i.text for i in self.tweets], "")
        self.permalink = [i.permalink for i in self.tweets]
        self._warned = False
        self._warn_dates_differ()
        
    def _warn_dates_differ(self):
        if self._warned:
            return
        for i in range(len(self.tweets) - 1):
            if self.tweets[i].date != self.tweets[i+1].date:
                logging.warning("dates of MultiTweet tweets differ")
                self._warned = True
                break
                
    def append(self, other):
        self.text += other.text
        self.tweets.append(other)
        self.permalink.append(other.permalink)
        self._warn_dates_differ()

class PolishTwitter:
    wojewodstwa_keywords = {
        r"śląski[a-z]*", r"mazowiecki[a-z]*", r"łódzki[a-z]*", r"dolnośląski[a-z]*",
        r"małopolski[a-z]*", r"podlaski[a-z]*", r"lubelski[a-z]*", r"lubuski[a-z]*",
        r"pomorski[a-z]*", r"wielkopolski[a-z]*", r"kujawsko-pomorski[a-z]*",
        r"zachodniopomorski[a-z]*", r"świętokrzyski[a-z]*", r"opolski[a-z]*",
        r"warmińsko-mazurski[a-z]*", r"podkarpacki[a-z]*"}
    @staticmethod
    def _daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)
    def __init__(self):
        self._log = logging.getLogger(self.__class__.__name__)
        self._username = "MZ_GOV_PL"
        self._start = datetime(2020,6,1)#datetime(2020,3,1)
        self._end = datetime.now()#datetime(2020,3,10)#datetime.now()
        self._base_criteria = got3.manager.TweetCriteria()\
            .setUsername(self._username)
            #.setMaxTweets(100)
    def __iter__(self):
        self._log.info("iterating over tweets")
        for dt in self._daterange(self._start, self._end):
            self._log.info(f"fetching tweets from {dt}")
            criteria = self._base_criteria\
                .setSince(dt.strftime("%Y-%m-%d"))\
                .setUntil((dt + timedelta(1)).strftime("%Y-%m-%d"))
            tweets = got3.manager.TweetManager.getTweets(criteria)
            tweets = sorted([tweet for tweet in tweets], key = lambda i: i.date)
            for tweet in tweets:
                yield tweet
    
    def parseAll(self):
        self._partial1, self._partial2 = None, None
        #relevant_tweets = []
        keywords = {"dzienny raport", "mamy [0-9]+", "z przykrością", "liczba", "W ciągu doby wykonano"} | self.wojewodstwa_keywords
        mtweet2 = None
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
        if re.match(r".*z przykrością.*", tweet.text, re.IGNORECASE):
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
        if re.match(r".*koronawirus z województw.*", tweet.text, re.IGNORECASE) or contains_region_name:
            ftweet.flags["regions"] = True
            if re.match(r".*mamy.*,$", tweet.text, re.IGNORECASE):
                ftweet.flags["partial"] = True
                if self._partial2 is not None:
                    ftweet.flags["regions"] = True
                    ftweet.associated = self._partial2
                    self._partial2.associated = True
                    self._partial2 = None
                else:
                    self._partial1 = ftweet
            elif contains_region_name:
                ftweet.flags["partial"] = True
                if self._partial1 is not None:
                    self._partial1.associated = tweet
                    ftweet.associated = True
                    self._partial1 = None
                else:
                    self._partial2 = ftweet
                    
        
        if re.match(r".*,$", tweet.text.strip(), re.IGNORECASE):
            ftweet.flags["partial"] = True
            
        
            
        return ftweet
    

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    PLTwitter = PolishTwitter()
    reports = PLTwitter.parseAll()
    for ftweet in reports:
        print(ftweet)
    #for tweet in PL:
    #    print(tweet.date)
    #    print(tweet.text)
    #    print(dir(tweet))
    #    print(tweet.permalink)
    #    input('')