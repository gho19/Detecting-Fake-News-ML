import tweepy
import pandas as pd
import time

api_key = 'WAXwiSwrSs088l8g91iRf9Tpc'
api_secret = 'fO943Sq5b3ZCgxJAtcT0zouPxaKw2v4tjDd5eaQKuy7PkuC0r6'
access_token = '1331622750759206912-qNp944NdLVPzJNarRhkZGPhrrMXzxk'
access_token_secret = 'w1LeCyW37WRGr4DtzKe0YR7EXXwG0SI5Sy2IvenO5Bg5U'
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)

usernames = ['JoeBiden', 'realDonaldTrump', 'KamalaHarris', 'Mike_Pence']
count = 25 # number of Tweets to scrape
tweets_df = pd.DataFrame()

for name in usernames:
      try:     
            # Creation of query method using parameters
            tweets = tweepy.Cursor(api.user_timeline, id = name).items(count)
            
            # Pulling information from Tweets iterable object
            tweets_list = [['Twitter', name, tweet.text, tweet.created_at] for tweet in tweets]
            
            # Creation of dataframe from Tweets list
            # Add or remove columns as you remove tweet information

            tweets_df = tweets_df.append(pd.DataFrame(tweets_list))
            

      except BaseException as e:
            print('failed on_status,', str(e))
            time.sleep(3)

tweets_df.to_csv('election2020tweets.csv', index = False)


