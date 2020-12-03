import requests
import pandas as pd
import sqlite3
import os

# API Key: 61e924b119ab4e4294956f2da5d1d01c

url = ('http://newsapi.org/v2/top-headlines?country=us&apiKey=61e924b119ab4e4294956f2da5d1d01c')
response = requests.get(url)
data = response.json()

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


def getHighestId(cur, conn, column_name, table_name):
    cur.execute('SELECT {} FROM {}'.format(column_name, table_name))
    
    section_id_list = [int(tup[0]) for tup in cur.fetchall()]

    if section_id_list != []: 
        highest_id = max(section_id_list) + 1
    
    else:
        highest_id = 0
    
    conn.commit()
    return highest_id


# Setups the database to store data gathered for SI 206 Final Project
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__)).replace("/NewsAPI", '')
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


# Uses the NEWS API to retrieve live articles from all over the web. 
# Specifically, this function gathers the Source, Title, Description, Timestamp, and URL of the article.
# newsApiData() returns a list containing ['Source', 'Title', 'Decription', 'Timestamp', 'URL']
def newsApiData():
    # NOTE: API ONLY REFRESHES EVERY HOUR!!!
    entries = []

    for news in data['articles']:
        title = news['title'].split(' - ')
        source = news['source']['name']
        entries.append([title[1], title[0], news['description'], news['publishedAt'], news['url']])

    return entries


# Uploads data retrieved from the NEW API to 'news_api' table 
# newsApiTable() has data, a list, as a parameter, which is the data returned from newsApiData() 
def newsApiTable(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS news_api (ArticleId INTEGER PRIMARY KEY, Title TEXT, Description TEXT, Timestamp TEXT, Url TEXT, SourceId INTEGER)")

    # Check how many rows in DB Table
    cur.execute('SELECT COUNT(*) from news_api')
    cur_result = cur.fetchone()
    rows = cur_result[0]

    # Count for IDs
    # Check how many rows in database to set ArticleId
    if rows == 0: 
        data_count = 0
        
        for entry in range(len(data)):
            #cur.execute("SELECT SourceId FROM news_api_sources WHERE news_api_sources.Source = '{}'".format(data[entry][0]))
            sourceId = getSourceID(cur, conn, data[entry][0])
            cur.execute("INSERT INTO news_api (ArticleId, Title, Description, Timestamp, Url, SourceId) VALUES (?,?,?,?,?,?)", (data_count, data[entry][1], data[entry][2], data[entry][3], data[entry][4], sourceId))
            data_count += 1
        print("Added 20 new headlines to news_api table!")
        conn.commit()

    else: 
        # Generate UNIQUE ArticleId for each article
        cur.execute("SELECT * FROM news_api WHERE ArticleId = (SELECT MAX(ArticleId) FROM news_api)")
        data_count = cur.fetchone()[0] + 1 

        # Gets the first article from previous API refresh
        cur.execute('SELECT Title from news_api')
        cur_check = cur.fetchall()
        check = cur_check[rows - 20][0]

        # Check to see if data already in table
        if check == data[0][1]:
            print("API has not refreshed any new articles! Try again later!")
        else: 
            # Upload data to table
            for entry in range(len(data)):
                # cur.execute("SELECT SourceId FROM news_api_sources WHERE news_api_sources.SourceId = '{}'".format(data[entry][0]))
                sourceId = getSourceID(cur, conn, data[entry][0])
                cur.execute("INSERT INTO news_api (ArticleId, Title, Description, Timestamp, Url, SourceId) VALUES (?,?,?,?,?,?)", (data_count, data[entry][1], data[entry][2], data[entry][3], data[entry][4], sourceId))
                data_count += 1
            print("Added 20 new headlines to database!")
            conn.commit()

  
def fillAllNewsApiTables():
    cur, conn = setUpDatabase('finalProject.db')
    data = newsApiData()
    newsApiTable(data, cur, conn)

fillAllNewsApiTables()

# To run news_api, navigate to news_api directory 
# Type python3 news_api.py






