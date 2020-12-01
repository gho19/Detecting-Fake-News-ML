import requests
import pandas as pd
import sqlite3
import os

# API Key: 61e924b119ab4e4294956f2da5d1d01c

url = ('http://newsapi.org/v2/top-headlines?country=us&apiKey=61e924b119ab4e4294956f2da5d1d01c')
response = requests.get(url)
data = response.json()

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def newsApiData():
    entries = []

    for news in data['articles']:
        title = news['title'].split(' - ')
        source = news['source']['name']
        entries.append([source, title[0], news['description'], news['publishedAt'], news['url']])

    return entries


def newsApiSourcesTable(data):
    cur.execute("CREATE TABLE IF NOT EXISTS news_api_sources (SourceId INTEGER PRIMARY KEY, Source TEXT)")

    # Check how many rows in DB Table
    cur.execute('SELECT COUNT(*) from news_api_sources')
    cur_result = cur.fetchone()
    rows = cur_result[0]

    # Count for IDs
    # Check how many rows in database to set TweetId
    if rows == 0: 
        data_count = 1
    else: 
        cur.execute("SELECT * FROM news_api_sources WHERE SourceId = (SELECT MAX(SourceId) FROM news_api_sources)")
        data_count = cur.fetchone()[0] + 1     

    for entry in range(len(data)):
        cur.execute("INSERT INTO news_api_sources (SourceId, Source) VALUES (?,?)", (data_count, data[entry][0]))
        data_count += 1
    conn.commit()


def newsApiTable(data):
    cur.execute("CREATE TABLE IF NOT EXISTS news_api (ArticleId INTEGER PRIMARY KEY, Title TEXT, Description TEXT, Timestamp TEXT, Url TEXT, SourceId INTEGER, UNIQUE(Url), FOREIGN KEY (SourceId) REFERENCES news_api_sources (SourceId))")

    # Check how many rows in DB Table
    cur.execute('SELECT COUNT(*) from news_api')
    cur_result = cur.fetchone()
    rows = cur_result[0]

    # Count for IDs
    # Check how many rows in database to set TweetId
    if rows == 0: 
        data_count = 1
    else: 
        cur.execute("SELECT * FROM news_api WHERE ArticleId = (SELECT MAX(ArticleId) FROM news_api)")
        data_count = cur.fetchone()[0] + 1     
      
    name_count = 1

    for entry in range(len(data)):
        cur.execute("INSERT INTO news_api (ArticleId, Title, Description, Timestamp, Url, SourceId) VALUES (?,?,?,?,?,?)", (data_count, data[entry][1], data[entry][2], data[entry][3], data[entry][4], name_count))
        data_count += 1
        name_count += 1
    conn.commit()

cur, conn = setUpDatabase('news_api.db')
data = newsApiData()
newsApiSourcesTable(data)
newsApiTable(data)








