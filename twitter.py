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
    path = os.path.dirname(os.path.abspath(__file__)).replace("/Twitter", '')
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def getHighestId(cur, conn, column_name, table_name):
    cur.execute('SELECT {} FROM {}'.format(column_name, table_name))
    
    section_id_list = [int(tup[0]) for tup in cur.fetchall()]

    if section_id_list != []: 
        highest_id = max(section_id_list) + 1
    
    else:
        highest_id = 0
    
    conn.commit()
    return highest_id


def getSourceID(cur, conn, source_name):
    cur.execute('CREATE TABLE IF NOT EXISTS Sources (source_id INT, source_name TEXT)')
    
    cur.execute('SELECT source_id, source_name FROM Sources')
    
    id_name_tups = cur.fetchall()
    source_ids = [tup[0] for tup in id_name_tups]
    source_names = [tup[1] for tup in id_name_tups]

    # if we already have this source in the sources_table
    if source_name in source_names:
        cur.execute('SELECT source_id FROM Sources WHERE Sources.source_name = "{}"'.format(source_name))
        source_id = cur.fetchone()[0]
        
    # if we don't already have this source in the sources table
    else:
        highest_id = getHighestId(cur, conn, 'source_id', 'Sources')
        cur.execute('INSERT INTO Sources (source_id, source_name) VALUES (?,?)', (highest_id, source_name))
        source_id = highest_id
    
    conn.commit()
    return source_id


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
# twitterUsersTable() has a list of Twitter usernams as a parameter 
def twitterUsersTable(usernames, cur, conn):
      cur.execute("DROP TABLE IF EXISTS Twitter_Users")
      cur.execute("CREATE TABLE IF NOT EXISTS Twitter_Users (UserId INTEGER PRIMARY KEY, Username TEXT)")

      for name in range(len(usernames)):
            cur.execute("INSERT INTO Twitter_Users (UserId, Username) VALUES (?,?)", (name, usernames[name]))
            print("Added new user to Twitter_Users table!")
      conn.commit()
            

# Creates table and adds data scraped from TWITTER API to 'twitter'
# twitterTable() has a list of Twitter usernams as a parameter 
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
                  sourceId = getSourceID(cur, conn, 'Twitter')
                  cur.execute("INSERT INTO Twitter (TweetId, SourceId, TweetNum, Tweet, Timestamp, UserId) VALUES (?,?,?,?,?,?)", (data_count, sourceId, data[row][0], data[row][1], data[row][2], name_count,))
                  data_count += 1
            name_count += 1
            print("Added 25 new Tweets to Twitter table!")
            conn.commit()
            time.sleep(5)
            

# Setup DB
def fillAllTwitterTables():
      cur, conn = setUpDatabase('finalProject.db')

      # Usernames from Twitter to scrape Tweets from 
      # NOTE: SOMETIMES PREVENTS SCRAPING TRUMP'S TWITTER 
      usernames = ['JoeBiden', 'realDonaldTrump', 'KamalaHarris', 'Mike_Pence']

      twitterUsersTable(usernames, cur, conn)
      twitterTable(usernames, cur, conn)

fillAllTwitterTables()

# To run twitter.py, navigate to twitter directory 
# Type python3 twitter.py



      
      


