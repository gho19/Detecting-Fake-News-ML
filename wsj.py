import requests
import json
from bs4 import BeautifulSoup as bs
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import sqlite3
import argparse
import database

parser = argparse.ArgumentParser()
parser.add_argument('--month', type=int, choices=[x for x in range(7, 12)], required=True)
parser.add_argument('--day', type=int, choices=[x for x in range(1, 30)], required=True)
args = parser.parse_args()

# Initializes this instance of Chromedriver. Takes in the path to the chromedriver
# as well as an option to make the driver headless or not. If headless, the instance
# of chrome will not physically appear on your computer, similar to the way BeautifulSoup
# operates. If not headless, the chrome window will pop up on your computer and user will
# be able to see the script moving around the page and typing things. Returns a chromedriver instance.
def getChromeDriver(path, headless = False):
    
    if headless:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=path, options=chrome_options)
    else:
        driver = webdriver.Chrome(executable_path=path)
    
    return driver


# Given a chromedriver, navigates to the Wall Street Journal's login page and
# signs in with the email and password parameters. Need to sign in so we can 
# access the full article content. Returns None.
def loginWSJ(driver, base_url, email, password):

    print('Logging into the Wall Street Journal!\n')

    driver.get(base_url)
    driver.implicitly_wait(5)
    
    emailField = driver.find_element_by_class_name('username')
    emailField.send_keys(email)

    passwordField = driver.find_element_by_class_name('password')
    passwordField.send_keys(password)

    loginButton = driver.find_element_by_tag_name('button')
    loginButton.click()

    time.sleep(5)

# Takes in a connection to the database as input, along with a chromedriver instance
# and an integer for the month and day we are trying to scrape.
# Creates a new table in the database to hold data about each of the WSJ articles
# from July 2020 to November 2020 we will eventually be scraping. Table has columns source_id 
# (unique integer for the WSJ), article_id (unique integer for each WSJ article), url_extension 
# (url to get to each article), day, month, and year that the article was published.
# Fills this table with five articles from each day in 7/2020 through 11/2020. Returns None.
def fillWSJ_URL_Table(cur, conn, driver, month, day):
    # create the table w/ the desired columns if it does not exist already
    # source_id, article_id, url_extension, day, month, year
    if month == 7 and day == 1:
        cur.execute('DROP TABLE IF EXISTS WSJ_URL_Data')
    
    cur.execute('CREATE TABLE IF NOT EXISTS WSJ_URL_Data (source_id INT, article_id INT, url_extension TEXT UNIQUE, day INT, month INT, year INT)')
    
    article_id = database.getHighestId(cur, conn, 'article_id',  'WSJ_URL_Data')

            
    # format url with the dynamic month and day 
    archive_url = "https://www.wsj.com/news/archive/2020/{}/{}".format(str(month), str(day))
    
    try:
        
        # make a request to the archive_url formatted string
        driver.get(archive_url)

        # wait up to 10 seconds for the all of the article URLS to be rendered on the page
        driver.implicitly_wait(10)

        # put all of the articles published on this day into a list
        articles = driver.find_elements_by_tag_name('article')

        # print(len(articles))
        # return

        # iterate over the first 5 articles
        for article in articles[:25]:
            
            # get the url to this specific article
            url = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')[29:]

            # THIS IS A DUMMY VALUE
            # Once the News_Sources table is set up, query that table to figure out what the ID is for the WSJ    
            source_id = database.getSourceID(cur, conn, 'The Wall Street Journal')

            cur.execute('INSERT INTO WSJ_URL_Data (source_id, article_id, url_extension, day, month, year) VALUES (?, ?, ?, ?, ?, ?)', (source_id, article_id, url, day, month, 2020))

            article_id += 1
            print('Inserted one new article into WSJ_URL_Data for {}/{}/2020.\n'.format(month, day))
    
    except Exception as e:
        print("Error fetching article URLs from {}.\nError message:\n{}\n".format(archive_url, e))
        
    
    # commit the changes to the database
    conn.commit()        

# Takes in a connection to the database as input, along with a chromedriver instance
# and an integer for the month and day we are trying to scrape.
# Creates a second table to store the actual content of each WSJ article.
# Fetches the article_id and url_extension from WSJ_URL_Data table. Uses that 
# url to go to the article's link, scrape the article, and fill a new table in the 
# database which contains the article_id as well as the article_content. Returns None, modifies the datbase.
def fillWSJArticleContentTable(cur, conn, driver, month, day):
    # source_id (from table above), article_id (from table above), article_content (scraped with selenium)
    
    # create the table w/ the desired columns if it does not exist already
    if month == 7 and day == 1:
        cur.execute('DROP TABLE IF EXISTS WSJ_Article_Content')
    
    cur.execute('CREATE TABLE IF NOT EXISTS WSJ_Article_Content (source_id INT, article_id INT, article_content TEXT UNIQUE)')
    # cur.execute('DROP TABLE IF EXISTS Kaggle')
    
    cur.execute('SELECT article_id, url_extension FROM WSJ_URL_Data WHERE WSJ_URL_Data.month = "{}" and WSJ_URL_Data.day = "{}"'.format(month, day))
    
    # for every row in WSJ_URL_Data, fetch article_id and article_url
    urlTuples = cur.fetchall()

    sourceId = database.getSourceID(cur, conn, 'The Wall Street Journal')

    # for each article's tuple of data in WSJ_URL_Data
    for tup in urlTuples:
        # article_id is the first element in the tuple
        article_id = tup[0]

        # the partial url segment is the second element in the tuple
        partial_url = tup[1]

        url = "https://www.wsj.com/articles/{}".format(partial_url)

        try:
            # go to the url for this specific article
            driver.get(url)

            # wait at most fifteen seconds for the article content to render
            driver.implicitly_wait(15)

            # scrape the article content and replace all new lines with a space (so text is all on one line)
            articleContent = driver.find_element_by_class_name("article-content  ").text.replace('\n', ' ')
            cur.execute('INSERT INTO WSJ_Article_Content (source_id, article_id, article_content) VALUES (?,?, ?)', (sourceId, article_id, articleContent))
            print('Scraped Wall Street Journal article content for article number {}.\n'.format(article_id + 1))


        except:
            print("Error fetching article content for article number {}.\n".format(article_id))
    
    # commit the changes to the database
    conn.commit()

# Drives all functions pertaining to the Wall Street Journal. Takes in a month and day 
# as an integer so it knows what data to get using selenium.
def driveWSJ_db(month, day):
    # CHASE: /Users/chasegoldman/Desktop/Michigan/Fall2020/SI206/SI206-FINAL-PROJECT
    # GRANT: /Users/gho/Desktop/SI-206/Projects/FinalProject/SI206-FINAL-PROJECT
    driver = getChromeDriver("/Users/gho/Desktop/SI-206/Projects/FinalProject/SI206-FINAL-PROJECT/chromedriver_2", True)
    login_url = "https://accounts.wsj.com/login?target=https%3A%2F%2Fwww.wsj.com%2Fnews%2Farchive%2F2020%2F11%2F27"

    try:
        if month == 7:
            month_string = 'July'
        elif month == 8:
            month_string = 'August'
        elif month == 9:
            month_string = 'September'
        elif month == 10:
            month_string = 'October'
        else:
            month_string = 'November'

        print('Preparing to scrape Wall Street Journal Articles for {} {}, 2020.\n'.format(month_string, day))

        cur, conn = database.setUpDatabase('finalProject.db')
        fillWSJ_URL_Table(cur, conn, driver, month, day)
        loginWSJ(driver, login_url, 'gochase@umich.edu', 'SI206Final!')
        fillWSJArticleContentTable(cur, conn, driver, month, day)
        driver.quit()
    
    except Exception as e:
        print("Error while handling Wall Street Journal Data.\n Error message:\n{}\n".format(e))
        driver.quit()


driveWSJ_db(args.month, args.day)

# HOW TO RUN THIS PROGRAM:

# python wsj.py --month 7 --day 1 (25 Articles for July 1 2020)
# python wsj.py --month 7 --day 2 (25 Articles for July 2 2020)
# ... 
# python wsj.py --month 11 --day 29 (25 Articles for November 29 2020)
