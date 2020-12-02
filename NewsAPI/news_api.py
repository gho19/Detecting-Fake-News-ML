import requests
import pandas as pd
import sqlite3
import os

# API Key: 61e924b119ab4e4294956f2da5d1d01c

url = ('http://newsapi.org/v2/top-headlines?country=us&apiKey=61e924b119ab4e4294956f2da5d1d01c')
response = requests.get(url)
data = response.json()

# Setups the database to store data gathered for SI 206 Final Project
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


# Uses the NEWS API to retrieve live articles from all over the web. 
# Specifically, this function gathers the Source, Title, Description, Timestamp, and URL of the article.
# newsApiData() returns a list containing ['Source', 'Title', 'Decription', 'Timestamp', 'URL']
def newsApiData():
    entries = []

    for news in data['articles']:
        title = news['title'].split(' - ')
        source = news['source']['name']
        entries.append([title[1], title[0], news['description'], news['publishedAt'], news['url']])

    return entries

# Uploads data retrieved from the NEW API to 'news_api' table 
# newsApiTable() has data, a list, as a parameter, which is the data returned from newsApiData() 
def newsApiTable(data):
    cur.execute("CREATE TABLE IF NOT EXISTS news_api (ArticleId INTEGER PRIMARY KEY, Title TEXT, Description TEXT, Timestamp TEXT, Url TEXT, Source TEXT)")

    # Check how many rows in DB Table
    cur.execute('SELECT COUNT(*) from news_api')
    cur_result = cur.fetchone()
    rows = cur_result[0]

    # Count for IDs
    # Check how many rows in database to set TweetId
    if rows == 0: 
        data_count = 1
        
        for entry in range(len(data)):
            cur.execute("INSERT INTO news_api (ArticleId, Title, Description, Timestamp, Url, Source) VALUES (?,?,?,?,?,?)", (data_count, data[entry][1], data[entry][2], data[entry][3], data[entry][4], data[entry][0]))
            data_count += 1
        print("Added 20 new headlines to news_api table!")
        conn.commit()

    else: 
        # Generate UNIQUE ArticleId for each article
        cur.execute("SELECT * FROM news_api WHERE ArticleId = (SELECT MAX(ArticleId) FROM news_api)")
        data_count = cur.fetchone()[0] + 1 

        # Gets the first article from previous API refresh
        cur.execute('SELECT Title from news_api')
        cur_check = cur.fetchone()
        print(cur_check)
        print(rows)
        check = cur_check[rows - 20]  

        # Check to see if data already in table
        if check == data[0][1]:
            print("API has not refreshed any new articles! Try again later!")
        else: 
            # Upload data to table
            for entry in range(len(data)):
                cur.execute("INSERT INTO news_api (ArticleId, Title, Description, Timestamp, Url, Source) VALUES (?,?,?,?,?,?)", (data_count, data[entry][1], data[entry][2], data[entry][3], data[entry][4], data[entry][0]))
                data_count += 1
            print("Added 20 new headlines to database!")
            conn.commit()

      
   
cur, conn = setUpDatabase('news_api.db')
data = newsApiData()
newsApiTable(data)



'''
def newsApiSourcesTable(data):
    cur.execute("CREATE TABLE IF NOT EXISTS news_api_sources (SourceId INTEGER, Source TEXT)")

    # Check how many rows in DB Table
    cur.execute('SELECT COUNT(*) from news_api_sources')
    cur_result = cur.fetchone()
    rows = cur_result[0]

    source_list = []

    # Count for IDs
    # Check how many rows in database to set TweetId
    if rows == 0: 
        # Set SourceId count to 1
        data_count = 1

        # Only get unique list of sources
        set_sources_list = []

        # Gets all sources
        for source in data:
            set_sources_list.append(source[0])

        set_sources_list = set(set_sources_list)

        for source in set_sources_list:
            source_list.append(source)

        
        # Adds data to table
        for entry in range(len(source_list)):
            cur.execute("INSERT INTO news_api_sources (Source, SourceId) VALUES (?,?)", (source_list[entry], data_count))
            data_count += 1

        conn.commit()

    else: 
        # Gets SourceId count
        cur.execute("SELECT * FROM news_api_sources WHERE SourceId = (SELECT MAX(SourceId) FROM news_api_sources)")
        data_count = cur.fetchone()[0] + 1 
        print(data_count)

        # Gets sources already in DB 
        cur.execute("SELECT Source from news_api_sources")
        set_sources_list = cur.fetchall()
        set_sources_list = set(set_sources_list)
        for source in set_sources_list:
            source_list.append(source[0])

        print(source_list)
        print(len(source_list))


        # Get potential new sources from data
        new_set_sources_list = []
        new_source_list = []

        for source in data:
            new_set_sources_list.append(source[0])

        new_set_sources_list = set(new_set_sources_list)

        for source in new_set_sources_list:
            new_source_list.append(source)

        print('\n\n' + 'Recently Scraped Sources')
        print(new_source_list)
        print(len(new_source_list))

        counter = 0
        for new_source in new_source_list:
            for source in source_list:
                if new_source == source:
                    new_source_list.remove(new_source)


        print('\n\n' + 'Only New Sources')
        print(new_source_list)
        print(len(new_source_list))

        source_list = source_list + new_source_list

        print('\n\n' + 'All Sources')
        print(source_list)
        print(len(source_list))

        print('\n\n')
        print("Data Counter")
        print(data_count)
        # Adds data to table
        for i in range(data_count, len(source_list)):
            cur.execute("INSERT INTO news_api_sources (Source, SourceId) VALUES (?,?)", (source_list[i], data_count))
            data_count += 1

        conn.commit()
'''


