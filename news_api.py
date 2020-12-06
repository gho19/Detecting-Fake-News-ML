import requests
import pandas as pd
import sqlite3
import os
import database

# API Key: 61e924b119ab4e4294956f2da5d1d01c

url = ('http://newsapi.org/v2/top-headlines?country=us&category=technology&apiKey=61e924b119ab4e4294956f2da5d1d01c')
response = requests.get(url)
data = response.json()


# Uses the NEWS API to retrieve live articles from all over the web. 
# Specifically, this function gathers the Source, Title, Description, Timestamp, and URL of the article.
# newsApiData() returns a list containing ['Source', 'Title', 'Decription', 'Timestamp', 'URL']
def newsApiData():
    # NOTE: API ONLY REFRESHES EVERY HOUR!!!
    entries = []

    for news in data['articles']:
        title = news['title'].split(' - ')
        source = news['source']['name']
        entries.append([source, title[0], news['description'], news['publishedAt'], news['url']])

    return entries


# Uploads data retrieved from the NEW API to 'News_API' table 
# newsApiTable() has data, a list, as a parameter, which is the data returned from newsApiData() 
# and curr + conn (for connecting to database)
def newsApiTable(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS News_API (ArticleId INTEGER PRIMARY KEY, Title TEXT, Description TEXT, Timestamp TEXT, Url TEXT, SourceId INTEGER)")

    # Check how many rows in DB Table
    cur.execute('SELECT COUNT(*) from News_API')
    cur_result = cur.fetchone()
    rows = cur_result[0]

    # Count for IDs
    # Check how many rows in database to set ArticleId
    if rows == 0: 
        data_count = 0
        
        for entry in range(len(data)):
            sourceId = database.getSourceID(cur, conn, data[entry][0])
            cur.execute("INSERT INTO News_API (ArticleId, Title, Description, Timestamp, Url, SourceId) VALUES (?,?,?,?,?,?)", (data_count, data[entry][1], data[entry][2], data[entry][3], data[entry][4], sourceId))
            data_count += 1
        print("Added 20 new headlines to News_API table!")
        conn.commit()

    else: 
        # Generate UNIQUE ArticleId for each article
        cur.execute("SELECT * FROM News_API WHERE ArticleId = (SELECT MAX(ArticleId) FROM News_API)")
        data_count = cur.fetchone()[0] + 1 

        # Gets the first article from previous API refresh
        cur.execute('SELECT Title from News_API')
        cur_check = cur.fetchall()
        check = cur_check[rows - 20][0]

        # Check to see if data already in table
        if check == data[0][1]:
            print("API has not refreshed any new articles! Try again later!")
        else: 
            # Upload data to table
            for entry in range(len(data)):
                sourceId = database.getSourceID(cur, conn, data[entry][0])
                cur.execute("INSERT INTO News_API (ArticleId, Title, Description, Timestamp, Url, SourceId) VALUES (?,?,?,?,?,?)", (data_count, data[entry][1], data[entry][2], data[entry][3], data[entry][4], sourceId))
                data_count += 1
            print("Added 20 new headlines to database!")
            conn.commit()

# Connects to database and inserts data into 'News_API' table  
def fillAllNewsApiTables():
    cur, conn = database.setUpDatabase('finalProject.db')
    data = newsApiData()
    newsApiTable(data, cur, conn)

fillAllNewsApiTables()

# To run News_API, navigate to News_API directory 
# Type python3 news_api.py