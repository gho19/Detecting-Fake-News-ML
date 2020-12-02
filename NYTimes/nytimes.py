import requests
import json
from bs4 import BeautifulSoup as bs
import csv
import time
import os
import sqlite3


# going to need this function at the top of all our files that insert data into the database
# make sure that the path to the database is correct
 
def connectToDB(db_name):
    path = os.path.dirname(os.path.abspath(__file__)).replace("/NYTimes", '')
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


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
    # need to store the sections that are already in the table
    cur.execute('SELECT section_name FROM NYT_Sections')
    all_sections = [tup[0] for tup in cur.fetchall()]
    new_sections = []
    for section in list_sections:
        if section not in all_sections:
            new_sections.append(section)
    
    return new_sections
    
def getHighestId(cur, conn, column_name, table_name):
    # need to store the max section_id in the table right now
    cur.execute('SELECT {} FROM {}'.format(column_name, table_name))
    
    section_id_list = [int(tup[0]) for tup in cur.fetchall()]

    if section_id_list != []: 
        highest_id = max(section_id_list) + 1
    else:
        highest_id = 0
    
    return highest_id

def fillNYT_Sections_Table(cur, conn, list_sections, runIteration):
    if runIteration == 0:
        cur.execute('DROP TABLE IF EXISTS NYT_Sections')
    
    cur.execute('CREATE TABLE IF NOT EXISTS NYT_Sections (section_id INT, section_name TEXT)')

    # need to store the sections that are already in the table
    new_sections = getNewSections(cur, conn, list_sections)

    # need to store the max section_id in the table right now
    highest_id = getHighestId(cur, conn, 'section_id', 'NYT_Sections')


    for i, section in enumerate(new_sections):
        cur.execute('INSERT INTO NYT_Sections (section_id, section_name) VALUES (?,?)', (i + highest_id, section))
    
    conn.commit()


def fillNYT_URL_Data_Table(cur, conn, data_dictionary, runIteration):
    if runIteration == 0:
        cur.execute('DROP TABLE IF EXISTS NYT_URL_Data')
    
    cur.execute('CREATE TABLE IF NOT EXISTS NYT_URL_Data (article_id INT, url_extension TEXT, section_id INT, word_count INT, print_page INT, day INT, month INT, year INT)')

    # need to store the max section_id in the table right now
    highest_id = getHighestId(cur, conn, 'article_id', 'NYT_URL_Data')

    for i, url in enumerate(data_dictionary):

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

        cur.execute('INSERT INTO NYT_URL_Data (article_id, url_extension, section_id, word_count, print_page, day, month, year) VALUES (?,?,?,?,?,?,?,?)', (article_id + highest_id, url_extension, section_id, word_count, print_page, day, month, year))
    
    conn.commit()


def fillNYTimes_ArticleContent_Table(cur, conn, runIteration):
    if runIteration == 0:
        cur.execute('DROP TABLE IF EXISTS NYT_ArticleContent')
    
    cur.execute('CREATE TABLE IF NOT EXISTS NYT_ArticleContent (article_id INT, article_content TEXT)')
    
    cur.execute('SELECT article_id, url_extension FROM NYT_URL_Data')


    id_url_tuples = cur.fetchall()

    for tup in id_url_tuples:
        
        article_id = tup[0]
        article_url_extension = tup[1]

        url = 'https://www.nytimes.com/' + article_url_extension

        try:
            resp = requests.get(url)
            soup = bs(resp.text, 'html.parser')
            story_content = soup.find('section', {'name':"articleBody"}).text.replace('\n', '')

            cur.execute('INSERT INTO NYT_ArticleContent (article_id, article_content) VALUES (?,?)', (article_id, story_content))
        
        except:
            print('Exception while handling NYT article number {}.\n'.format(article_id))
            continue

    conn.commit()


def getNYTURLDictionary(enforceLimit, runIteration):

    all_data_dictionary = {}

    if enforceLimit:
        count = 0
        startingIndex = runIteration * 26
    else:
        startingIndex = 110

    
    # loop through the years 2015 and 2016
    for year in range(2015, 2017)[:1]:
        # loop through every other month between january and december
        for month in range(1, 13, 2)[:1]:
            date_dictionary = {}

            # sleep for a second so we don't overwhelm the API
            time.sleep(1)

            # format the base url with the correct date and API key
            base_url = "https://api.nytimes.com/svc/archive/v1/{}/{}.json?api-key={}".format(str(year), str(month), API_KEY, 20)

            # make a request to the server
            resp = requests.get(base_url)

            # turn the response request into a dictionary of data
            data_dict = json.loads(resp.text)

            # iterate over each mini dictionary in the response
            for mini_dict in data_dict["response"]["docs"][startingIndex:]:
                
                # try to pull out the correct data from the dictionary
                try:
                    # get the url extension for this article
                    url = mini_dict["web_url"].strip('https://www.nytimes.com/')
                    # print(url)
                    
                    # get the date this article was published
                    pub_date = mini_dict['pub_date']

                    # parse the data into a better formula
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
                    
                    # check to see if we have reached 25 new things
                    if enforceLimit:
                        count += 1
                        if count >= 25:
                            
                            # HELPER CODE
                            for url in all_data_dictionary:
                                print(url)

                            # HELPER CODE


                            return all_data_dictionary

                # if there was a key error or some other issue, just continue onto the next dictionary
                except:
                    continue
    
    return all_data_dictionary


def fillAllNYT_Tables(cur, conn, enforceLimit, runIteration):
    
    # pull the data from NYTimes API and put it into a dictionary
    nytimes_url_dictionary = getNYTURLDictionary(enforceLimit, runIteration)
    # print(nytimes_url_dictionary)

    # fill the section_id table with data from the dictionary
    section_set = set()

    for url in nytimes_url_dictionary:
        section_set.add(nytimes_url_dictionary[url]['section_name'])
    
    fillNYT_Sections_Table(cur, conn, list(section_set), runIteration)

    # fill the main URL Data dictionary
    fillNYT_URL_Data_Table(cur, conn, nytimes_url_dictionary, runIteration)

    # # fill the Table with Article Content
    # fillNYTimes_ArticleContent_Table(cur, conn, runIteration)

def driveNYT_db(enforceLimit = True, runIteration = 0):
    cur, conn = connectToDB('finalProject.db')
    fillAllNYT_Tables(cur, conn, enforceLimit, runIteration)

driveNYT_db(True, 2)

# first run at the command line:
# python nytimes.py (enforceLimit = True, runIteration = 0)
# python nytimes.py (enforceLimit = True, runIteration = 1)
# python nytimes.py (enforceLimit = True, runIteration = 2)
# python nytimes.py (enforceLimit = True, runIteration = 3)
# python nytimes.py (enforceLimit = False, runIteration = 4)



