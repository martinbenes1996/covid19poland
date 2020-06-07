
from datetime import datetime,timedelta
import logging
from functools import reduce
import re

import GetOldTweets3 as got3

class MultiTweet:
    def __init__(self, *args):
        self.tweets = args
        self.text = reduce(lambda a,i: a+i, [i.text for i in self.tweets], "")
        self.permalink = [i.permalink for i in self.tweets]

class PolishTwitter:
    wojewodstwa_keywords = {
        "śląskiego", "mazowieckiego", "łódzkiego", "dolnośląskiego",
        "małopolskiego", "podlaskiego", "lubelskiego", "lubuskiego",
        "pomorskiego", "wielkopolskiego", "kujawsko-pomorskiego",
        "zachodniopomorskiego", "świętokrzyskiego", "opolskiego",
        "warmińsko-mazurskiego", "podkarpackiego"}
    @staticmethod
    def _daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
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
        relevant_tweets = []
        keywords = {"dzienny raport", "mamy [0-9]+", "z prykrością", "liczba"} | self.wojewodstwa_keywords
        for tweet in self:
            for kw in keywords:
                if re.match(f".*{kw}.*", tweet.text, re.IGNORECASE):
                    if re.match(f"{self.wojewodstwa_keywords}.*", relevant_tweets[-1].text, re.IGNORECASE):
                        
                        relevant_tweets.append(tweet)
                    
                    break
        
        for tweet in relevant_tweets:
            
        return reports

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    PLTwitter = PolishTwitter()
    reports = PLTwitter.parseAll()
    for report in reports:
        print(report.permalink)
        print(report.text)
        input('')
    #for tweet in PL:
    #    print(tweet.date)
    #    print(tweet.text)
    #    print(dir(tweet))
    #    print(tweet.permalink)
    #    input('')