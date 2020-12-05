import tweepy
import pandas as pd
import time
import sqlite3
import os
import database

api_key = 'WAXwiSwrSs088l8g91iRf9Tpc'
api_secret = 'fO943Sq5b3ZCgxJAtcT0zouPxaKw2v4tjDd5eaQKuy7PkuC0r6'
access_token = '1331622750759206912-qNp944NdLVPzJNarRhkZGPhrrMXzxk'
access_token_secret = 'w1LeCyW37WRGr4DtzKe0YR7EXXwG0SI5Sy2IvenO5Bg5U'
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)


# Uses the TWITTER API (tweepy) to retrieve Tweets from a specified user.
# This function gathers a unique Tweet ID, the Tweet text, and Timestamp of the Tweet
# twitterData() takes a username as a parameter (i.e. realDonaldTrump)
# twitterData() returns a list containing ['tweetId', 'tweetText', 'tweetTimestamp']
def twitterData(user):
      # Number of Tweets to scrape per user
      count = 25

      data = []

      try:     
            # Creation of query method using parameters
            tweets = tweepy.Cursor(api.user_timeline, id = user).items(count)
                  
            # Pulling information from Tweets iterable object
            # tweet_list only contains 25 data points per Twitter user
            tweets_list = [[tweet.id, tweet.text.strip(), tweet.created_at] for tweet in tweets]
            for i in range(len(tweets_list)):
                  data.append(tweets_list[i])
            
      except BaseException as e:
            print('failed on_status,', str(e))
            time.sleep(3)

      return data


# Creates table and uploads data to table called 'twitter_users' with UserId and Username as columns
# twitterUsersTable() has a list of Twitter usernams as a parameter and curr + conn (for connecting to database)
def twitterUsersTable(usernames, cur, conn):
      cur.execute("DROP TABLE IF EXISTS Twitter_Users")
      cur.execute("CREATE TABLE IF NOT EXISTS Twitter_Users (UserId INTEGER PRIMARY KEY, Username TEXT)")

      for name in range(len(usernames)):
            cur.execute("INSERT INTO Twitter_Users (UserId, Username) VALUES (?,?)", (name, usernames[name]))
            print("Added new user to Twitter_Users table!")
      conn.commit()
            

# Creates table and adds data scraped from TWITTER API to 'twitter'
# twitterTable() has a list of Twitter usernames as a parameter and curr + conn (for connecting to database)
# The columns in the database are as follows: TweetId, Tweet, Timestamp, TweetNum, UserId
def twitterTable(usernames, cur, conn):
      cur.execute("DROP TABLE IF EXISTS Twitter")
      cur.execute("CREATE TABLE IF NOT EXISTS Twitter (TweetId INTEGER PRIMARY KEY, SourceId INTEGER, Tweet TEXT, Timestamp TEXT, TweetNum INTEGER, UserId INTEGER, UNIQUE(TweetNum), FOREIGN KEY (UserId) REFERENCES Twitter_Users (UserId))")

      # Check how many rows in DB Table
      cur.execute('SELECT COUNT(*) from Twitter')
      cur_result = cur.fetchone()
      rows = cur_result[0]

      # Count for IDs
      # Check how many rows in database to set TweetId
      if rows == 0: 
            data_count = 0
      else: 
            cur.execute("SELECT * FROM Twitter WHERE TweetId = (SELECT MAX(TweetId) FROM Twitter)")
            data_count = cur.fetchone()[0] + 1     
      
      for name in usernames:
            # Scrape Twitter based upon username
            data = twitterData(name)
            cur.execute("SELECT UserId FROM Twitter_Users WHERE Twitter_Users.Username = '{}'".format(name))
            name_count = cur.fetchone()[0]
            # Setup database
            for row in range(len(data)):
                  sourceId = database.getSourceID(cur, conn, 'Twitter')
                  cur.execute("INSERT INTO Twitter (TweetId, SourceId, TweetNum, Tweet, Timestamp, UserId) VALUES (?,?,?,?,?,?)", (data_count, sourceId, data[row][0], data[row][1], data[row][2], name_count,))
                  data_count += 1
            name_count += 1
            print("Added 25 new Tweets to Twitter table!")
            conn.commit()
            time.sleep(5)
            

# Connects to database and inserts data into 'Twitter' table  
def fillAllTwitterTables():
      cur, conn = database.setUpDatabase('finalProject.db')

      # Usernames from Twitter to scrape Tweets from 
      # NOTE: SOMETIMES PREVENTS SCRAPING TRUMP'S TWITTER 
      usernames = ['JoeBiden', 'realDonaldTrump', 'KamalaHarris', 'Mike_Pence']
      twitterUsersTable(usernames, cur, conn)
      twitterTable(usernames, cur, conn)

fillAllTwitterTables()

# To run twitter.py, navigate to twitter directory 
# Type python3 twitter.py



      
      


