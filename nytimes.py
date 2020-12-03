import requests
import json
from bs4 import BeautifulSoup as bs
import csv
import time
import os
import sqlite3
import argparse
import database 



parser = argparse.ArgumentParser()
parser.add_argument('--numRuns', type=int, choices=[x for x in range(25)], required=True)
args = parser.parse_args()

# This script is collecting the URLS for all articles published by the New York Times
# in 2015 and 2016 (before Trump and the first year of Trump). 
# Then, there will be another script that scrapes the text content from each article URL and
# puts that text content into the database

API_KEY = "JdfhwcfpxaR5uHaqRSpZMSxuxsA78twm"
good_section_names = ['U.S.', 'World', 'Science', 'Today’s Paper', 'New York', 'Health', 'Politics']

def parsePubDate(pubDate):
    #2015-01-01T00:03:50+0000
    split_date = pubDate.split('-')
    year = int(split_date[0])
    month = int(split_date[1])
    day = int(split_date[2].split('T')[0])
    return day, month, year

def getNewSections(cur, conn, list_sections):
    cur.execute('SELECT section_name FROM NYT_Sections')
    
    all_sections = [tup[0] for tup in cur.fetchall()]
    new_sections = []
    
    for section in list_sections:
        
        if section not in all_sections:
            new_sections.append(section)
    
    conn.commit()
    return new_sections


def fillNYT_Sections_Table(cur, conn, list_sections, runIteration):
    if runIteration == 0:
        cur.execute('DROP TABLE IF EXISTS NYT_Sections')
    
    cur.execute('CREATE TABLE IF NOT EXISTS NYT_Sections (section_id INT, section_name TEXT)')

    # need to store the sections that are already in the table
    new_sections = getNewSections(cur, conn, list_sections)

    # need to store the max section_id in the table right now
    highest_id = database.getHighestId(cur, conn, 'section_id', 'NYT_Sections')


    for i, section in enumerate(new_sections):
        cur.execute('INSERT INTO NYT_Sections (section_id, section_name) VALUES (?,?)', (i + highest_id, section))
    
    conn.commit()


def fillNYT_URL_Data_Table(cur, conn, data_dictionary, runIteration):
    if runIteration == 0:
        cur.execute('DROP TABLE IF EXISTS NYT_URL_Data')
    
    cur.execute('CREATE TABLE IF NOT EXISTS NYT_URL_Data (source_id INT, article_id INT, url_extension TEXT, section_id INT, word_count INT, print_page INT, day INT, month INT, year INT)')

    # need to store the max section_id in the table right now
    highest_id = database.getHighestId(cur, conn, 'article_id', 'NYT_URL_Data')

    for i, url in enumerate(data_dictionary):

        source_id = database.getSourceID(cur, conn, 'New York Times')
        article_id = i
        url_extension = url

        section_name = data_dictionary[url]['section_name']
        
        cur.execute('SELECT section_id FROM NYT_Sections WHERE NYT_Sections.section_name = "{}"'.format(section_name))

        section_id = cur.fetchone()[0]

        word_count = data_dictionary[url]['word_count']
        
        print_page = data_dictionary[url]['print_page']

        day = data_dictionary[url]['day']

        month = data_dictionary[url]['month']

        year = data_dictionary[url]['year']

        cur.execute('INSERT INTO NYT_URL_Data (source_id, article_id, url_extension, section_id, word_count, print_page, day, month, year) VALUES (?,?,?,?,?,?,?,?,?)', (source_id, article_id + highest_id, url_extension, section_id, word_count, print_page, day, month, year))
        print('Inserted NYTimes article number {} into the NYTimes URL Data Table.\n'.format(i))
    
    conn.commit()


def fillNYTimes_ArticleContent_Table(cur, conn, runIteration):
    if runIteration == 0:
        cur.execute('DROP TABLE IF EXISTS NYT_ArticleContent')
    
    startingIndex = runIteration * 25
    
    cur.execute('CREATE TABLE IF NOT EXISTS NYT_ArticleContent (source_id INT, article_id INT, article_content TEXT)')
    
    cur.execute('SELECT source_id, article_id, url_extension FROM NYT_URL_Data')

    # on runIteration 1, need to only select url_extensions 25 - 50

    id_url_tuples = cur.fetchall()

    for tup in id_url_tuples[startingIndex:]:
        
        source_id = tup[0]
        article_id = tup[1]
        article_url_extension = tup[2]

        url = 'https://www.nytimes.com/' + article_url_extension

        try:
            resp = requests.get(url)
            soup = bs(resp.text, 'html.parser')
            story_content = soup.find('section', {'name':"articleBody"}).text.replace('\n', '')

            cur.execute('INSERT INTO NYT_ArticleContent (source_id, article_id, article_content) VALUES (?,?,?)', (source_id, article_id, story_content))
            print('Scraped article content for NYTimes article number {} and insert into NYTimes Article Content Table.\n'.format(article_id))
        
        except:
            # print('Exception while handling NYT article number {}.\n'.format(article_id))
            continue

    conn.commit()


def getNYTURLDictionary(runIteration):

    all_data_dictionary = {}
    date_dictionary = {}
    
    month = runIteration + 1
    count = 0
    maxCount = 25
    
    if month >= 1 and month <= 12:
        year = 2015
    else:
        year = 2016
        month = month - 12
            
    # sleep for a second so we don't overwhelm the API
    time.sleep(1)

    # format the base url with the correct date and API key
    base_url = "https://api.nytimes.com/svc/archive/v1/{}/{}.json?api-key={}".format(str(year), str(month), API_KEY)

    # make a request to the server
    resp = requests.get(base_url)

    # turn the response request into a dictionary of data
    data_dict = json.loads(resp.text)

    # iterate over each mini dictionary in the response
    # for mini_dict in data_dict["response"]["docs"][startingIndex:]:
    for mini_dict in data_dict["response"]["docs"]:
        
        # try to pull out the correct data from the dictionary
        try:
            
            # get the url extension for this article
            url = mini_dict["web_url"].strip('https://www.nytimes.com/')
            # print(url)
            
            # get the date this article was published
            pub_date = mini_dict['pub_date']

            # parse the date into a better format
            day, month, year = parsePubDate(pub_date)

            # get the name of the section that this article belongs to
            section_name = mini_dict['section_name']

            # get rid of articles that aren't politically related at all
            if section_name not in good_section_names:
                continue
            
            # checking to make sure we only get 2 articles (at most) from each day
            day_month_year_string = '{}/{}/{}'.format(day, month, year)
            
            if day_month_year_string not in date_dictionary:
                date_dictionary[day_month_year_string] = 1
            
            else:
                date_dictionary[day_month_year_string] += 1
                
                if date_dictionary[day_month_year_string] > 2:
                    continue

            # get the wordCount for this article
            wordCount = int(mini_dict['word_count'])

            # get the page number that this article was printed on
            printPage = int(mini_dict['print_page'])
            
            # add a new entry to the dictionary for this article
            all_data_dictionary[url] = {'section_name': section_name, 'word_count': wordCount, 'print_page': printPage, 'day': day, 'month': month, 'year': year}
            
            # check to see if we have reached max_limit new things
            count += 1
            if count >= maxCount:
                return all_data_dictionary

        # if there was a key error or some other issue, just continue onto the next dictionary
        except:
            # print('Exception while handling NYTimes dictionary data.\n')
            continue

    return all_data_dictionary


def fillAllNYT_Tables(cur, conn, runIteration):
    
    # pull the data from NYTimes API and put it into a dictionary
    print('Pulling data from the NYTimes API for run number {}\n'.format(runIteration + 1))
    nytimes_url_dictionary = getNYTURLDictionary(runIteration)
    # print(nytimes_url_dictionary)

    # fill the section_id table with data from the dictionary
    section_set = set()

    for url in nytimes_url_dictionary:
        section_set.add(nytimes_url_dictionary[url]['section_name'])
    
    print('Filling the NYTimes Section table with each unique section.\n')
    fillNYT_Sections_Table(cur, conn, list(section_set), runIteration)

    # fill the main URL Data dictionary
    print('Filling the NYTimes URL Data table with data about each of the 25 articles.\n')
    fillNYT_URL_Data_Table(cur, conn, nytimes_url_dictionary, runIteration)

    # fill the Table with Article Content
    print('Scraping article content for each of the 25 articles in the NYTimes URL Data table.\n')
    fillNYTimes_ArticleContent_Table(cur, conn, runIteration)

def driveNYT_db(runIteration):
    cur, conn = database.setUpDatabase('finalProject.db')
    fillAllNYT_Tables(cur, conn, runIteration)

driveNYT_db(args.numRuns)

# HOW TO RUN THIS PROGRAM AT THE COMMAND LINE:
# 1) python nytimes.py --numRuns 0 (25 Articles for January 2015)
# 2) python nytimes.py --numRuns 1 (25 Articles for February 2015)
# 3) python nytimes.py --numRuns 2 (25 Articles for March 2015)
# 4) python nytimes.py --numRuns 3 (25 Articles for April 2015)
#    ....
# 24) python nytimes.py --numRuns 23 (25 Articles for December 2016)





