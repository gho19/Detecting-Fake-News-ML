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

      data = []

      for name in usernames:
            try:     
                  # Creation of query method using parameters
                  tweets = tweepy.Cursor(api.user_timeline, id = name).items(count)
                  
                  # Pulling information from Tweets iterable object
                  # tweet_list only contains 25 data points per Twitter user
                  tweets_list = [[name, tweet.text.strip(), tweet.created_at] for tweet in tweets]
                  for i in range(len(tweets_list)):
                        data.append(tweets_list[i])
            
            except BaseException as e:
                  print('failed on_status,', str(e))
                  time.sleep(3)

      return data

# Creates table in database with UserId and Username
def twitterUsersTable():
      cur.execute("DROP TABLE IF EXISTS twitter_users")
      cur.execute("CREATE TABLE twitter_users (UserId INTEGER PRIMARY KEY, Username TEXT)")

      # Usernames from Twitter to scrape Tweets from 
      usernames = ['JoeBiden', 'realDonaldTrump', 'KamalaHarris', 'Mike_Pence']

      for name in range(len(usernames)):
            cur.execute("INSERT INTO twitter_users (UserId, Username) VALUES (?,?)", (name + 1, usernames[name]))

# Creates table with raw data gathered from Twitter API
def twitterDataTable():
      data = twitterData()

      cur.execute("DROP TABLE IF EXISTS twitter_raw")
      cur.execute("CREATE TABLE twitter_raw (TweetId INTEGER PRIMARY KEY, Username TEXT, Tweet TEXT, Timestamp TEXT)")

      for row in range(len(data)):
            cur.execute("INSERT INTO twitter_raw (TweetId, Username, Tweet, Timestamp) VALUES (?,?,?,?)", (row + 1, data[row][0], data[row][1], data[row][2]))

      conn.commit()

# Creates table with JOIN operation, to avoid duplicate data
def twitterSharedUsersTable():
      cur.execute("DROP TABLE IF EXISTS twitter_final")
      cur.execute("CREATE TABLE twitter_final AS SELECT twitter_raw.TweetId, twitter_users.UserId, twitter_raw.Tweet, twitter_raw.Timestamp FROM twitter_raw JOIN twitter_users ON twitter_users.Username = twitter_raw.Username")
      conn.commit()


# DATA ENTRY TO DATABASE, CHANGE LATER WHEN FINAL.DB READY
'''
cur, conn = setUpDatabase('twitter.db')
twitterUsersTable()
twitterDataTable()
twitterSharedUsersTable()
'''



