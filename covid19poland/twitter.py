
from datetime import datetime,timedelta
import logging
from functools import reduce
import re

import GetOldTweets3 as got3

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
        "śląskiego", "mazowieckiego", "łódzkiego", "dolnośląskiego",
        "małopolskiego", "podlaskiego", "lubelskiego", "lubuskiego",
        "pomorskiego", "wielkopolskiego", "kujawsko-pomorskiego",
        "zachodniopomorskiego", "świętokrzyskiego", "opolskiego",
        "warmińsko-mazurskiego", "podkarpackiego"}
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
                    print(f"\033[92m{tweet.text}\033[00m")
                    info = self._classify_tweet(tweet)
                    yield info
                    #yield
                        
                    #if any(re.match(f"{wojw_kw}.*", tweet.text.strip(), re.IGNORECASE) for wojw_kw in self.wojewodstwa_keywords):
                    #    print("\t* multitweet (1)")
                    #    mtweet2 = tweet
                    #elif mtweet2 is not None:
                    #    print("\t* multitweet (2)")
                    #    relevant_tweets.append(MultiTweet(tweet, mtweet2))
                    #    mtweet2 = None
                    #    yield self._classify_tweet(relevant_tweets[-1])
                    #else:
                    #    relevant_tweets.append(tweet)
                    #    yield self._classify_tweet(relevant_tweets[-1])
                    #print(f"\033[92m{tweet.text[:min(len(tweet.text),80)]}\033[00m")
                    break
            else:
                pass
                print(f"\033[91m{tweet.text}\033[00m")
        
        #return relevant_tweets
        #return [self._classify_tweet(tweet) for tweet in relevant_tweets]

    def _classify_tweet(self, tweet):
        # daily report = rewrite manually from image
        if re.match(r".*dzienny raport.*", tweet.text, re.IGNORECASE):
            print("\t* Daily report")
            
        # death numbers    
        if re.match(r".*z przykrością.*", tweet.text, re.IGNORECASE):
            print("\t* Death numbers.")
            
        # test numbers
        if re.match(r".*w ciągu doby wykonano.*", tweet.text, re.IGNORECASE):
            print("\t* Test numbers.")
        
        # case numbers
        if re.match(r".*mamy [0-9]+ now[a-z]*.*", tweet.text, re.IGNORECASE):
            print("\t* Case numbers.")
        
        # cumulative cases
        if re.match(r".*liczba zakażonych koronawirusem.*", tweet.text, re.IGNORECASE):
            print("\t* Cumulative cases.")
            
        # regional data
        if re.match(r".*koronawirus z województw.*", tweet.text, re.IGNORECASE) or any(re.match(f".*{wojewodstwo}.*", tweet.text, re.IGNORECASE) for wojewodstwo in self.wojewodstwa_keywords):
            print("\t* Regional data.")
            if re.match(r".*mamy.*,$", tweet.text, re.IGNORECASE):
                print("\t* Partial tweet (1).")
                if self._partial2 is not None:
                    tweet = MultiTweet(tweet, self._partial2)
                    self._partial2 = None
                    if re.match(r".*,$", tweet.text, re.IGNORECASE):
                        pass
                        # third part
                    print(f"\t\tMERGED: {tweet.text}")
                else:
                    self._partial1 = tweet
                input('')
        if any(re.match(f"{wojw_kw}.*", tweet.text.strip(), re.IGNORECASE) for wojw_kw in self.wojewodstwa_keywords):
            print("\t* Partial tweet (2)")
            if self._partial1 is not None:
                tweet = MultiTweet(self._partial1, tweet)
                print(f"\t\tMERGED: {tweet.text}")
                self._partial1 = None
            else:
                self._partial2 = tweet 
            input('')
        
            
        return tweet
    

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    PLTwitter = PolishTwitter()
    reports = PLTwitter.parseAll()
    for report in reports:
        pass
    #for tweet in PL:
    #    print(tweet.date)
    #    print(tweet.text)
    #    print(dir(tweet))
    #    print(tweet.permalink)
    #    input('')