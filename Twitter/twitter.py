import tweepy
import pandas as pd
import time
import sqlite3
import os

api_key = 'WAXwiSwrSs088l8g91iRf9Tpc'
api_secret = 'fO943Sq5b3ZCgxJAtcT0zouPxaKw2v4tjDd5eaQKuy7PkuC0r6'
access_token = '1331622750759206912-qNp944NdLVPzJNarRhkZGPhrrMXzxk'
access_token_secret = 'w1LeCyW37WRGr4DtzKe0YR7EXXwG0SI5Sy2IvenO5Bg5U'
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def twitterData():
      # Usernames from Twitter to scrape Tweets from 
      usernames = ['JoeBiden', 'realDonaldTrump', 'KamalaHarris', 'Mike_Pence']

      # Number of Tweets to scrape per user
      count = 25 

      # tweets_df = pd.DataFrame()

      data = []

      for name in usernames:
            try:     
                  # Creation of query method using parameters
                  tweets = tweepy.Cursor(api.user_timeline, id = name).items(count)
                  
                  # Pulling information from Tweets iterable object
                  tweets_list = [[name, tweet.text.strip(), tweet.created_at] for tweet in tweets]
                  for i in range(len(tweets_list)):
                        data.append(tweets_list[i])
                  
                  # Creation of dataframe from Tweets list
                  # Add or remove columns as you remove tweet information
                  # tweets_df = tweets_df.append(pd.DataFrame(tweets_list))
                  

            except BaseException as e:
                  print('failed on_status,', str(e))
                  time.sleep(3)

      return data

def insertTwitterData():
      cur, conn = setUpDatabase('twitter.db')
      data = twitterData()

      cur.execute("DROP TABLE IF EXISTS Twitter")
      cur.execute("CREATE TABLE Twitter (tweet_id INTEGER PRIMARY KEY, username TEXT, tweet TEXT, timestamp TEXT)")

      for row in range(len(data)):
            cur.execute("INSERT INTO Twitter (tweet_id, username, tweet, timestamp) VALUES (?,?,?,?)", (row, data[row][0], data[row][1], data[row][2]))

      conn.commit()

insertTwitterData()

