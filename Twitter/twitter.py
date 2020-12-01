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

def twitterData(user):
      # Number of Tweets to scrape per user
      count = 25

      data = []

      try:     
            # Creation of query method using parameters
            tweets = tweepy.Cursor(api.user_timeline, id = user, since_id = '1/1/2020').items(count)
                  
            # Pulling information from Tweets iterable object
            # tweet_list only contains 25 data points per Twitter user
            tweets_list = [[tweet.id, tweet.text.strip(), tweet.created_at] for tweet in tweets]
            for i in range(len(tweets_list)):
                  data.append(tweets_list[i])
            
      except BaseException as e:
            print('failed on_status,', str(e))
            time.sleep(3)

      return data


# Creates table in database with UserId and Username
def twitterUsersTable(usernames):
      cur.execute("CREATE TABLE IF NOT EXISTS twitter_users (UserId INTEGER PRIMARY KEY, Username TEXT)")

      for name in range(len(usernames)):
            cur.execute("INSERT INTO twitter_users (UserId, Username) VALUES (?,?)", (name + 1, usernames[name]))
            conn.commit()



# Creates table and adds data scraped from API
def twitterTable(usernames):
      cur.execute("CREATE TABLE IF NOT EXISTS twitter (TweetId INTEGER PRIMARY KEY, Tweet TEXT, Timestamp TEXT, TweetNum INTEGER, UserId INTEGER, UNIQUE(TweetNum), FOREIGN KEY (UserId) REFERENCES twitter_users (UserId))")

      # Check how many rows in DB Table
      cur.execute('SELECT COUNT(*) from twitter')
      cur_result = cur.fetchone()
      rows = cur_result[0]

      # Count for IDs
      # Check how many rows in database to set TweetId
      if rows == 0: 
            data_count = 1
      else: 
            cur.execute("SELECT * FROM twitter WHERE TweetId = (SELECT MAX(TweetId) FROM twitter)")
            data_count = cur.fetchone()[0] + 1     
      
      name_count = 1

      for name in usernames:
            # Scrape Twitter based upon username
            data = twitterData(name)

            # Setup database
            for row in range(len(data)):
                  cur.execute("INSERT INTO twitter (TweetId, TweetNum, Tweet, Timestamp, UserId) VALUES (?,?,?,?,?)", (data_count, data[row][0], data[row][1], data[row][2], name_count,))
                  data_count += 1
            name_count += 1
            conn.commit()
            time.sleep(5)
            

# Setup DB
cur, conn = setUpDatabase('twitter.db')

# Usernames from Twitter to scrape Tweets from 
usernames = ['JoeBiden', 'realDonaldTrump', 'KamalaHarris', 'Mike_Pence']

twitterUsersTable(usernames)
twitterTable(usernames)



      
      


