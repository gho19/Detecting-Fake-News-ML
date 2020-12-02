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


# Connects this file to the database.
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__)).replace("/WSJ", '')
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# Initializes this instance of Chromedriver. Takes in the path to the chromedriver
# as well as an option to make the driver headless or not. If headless, the instance
# of chrome will not physically appear on your computer, similar to the way BeautifulSoup
# operates. If not headless, the chrome window will pop up on your computer and user will
# be able to see the script moving around the page and typing things.
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
# access the full article content.
def loginWSJ(driver, base_url, email, password):

    driver.get(base_url)
    driver.implicitly_wait(5)
    
    emailField = driver.find_element_by_class_name('username')
    emailField.send_keys(email)

    passwordField = driver.find_element_by_class_name('password')
    passwordField.send_keys(password)

    loginButton = driver.find_element_by_tag_name('button')
    loginButton.click()

    time.sleep(5)

# Creates a new table in the database to hold data about each of the WSJ articles
# from July 2020 to November 2020 we will eventually be scraping. Table has columns source_id 
# (unique integer for the WSJ), article_id (unique integer for each WSJ article), url_extension 
# (url to get to each article), day, month, and year that the article was published.
# Fills this table with five articles from each day in 7/2020 through 11/2020.
def fillWSJ_URL_Table(cur, conn, driver):
    # create the table w/ the desired columns if it does not exist already
    # source_id, article_id, url_extension, day, month, year
    # cur.execute('DROP TABLE IF EXISTS WSJ_URL_Data')
    cur.execute('CREATE TABLE IF NOT EXISTS WSJ_URL_Data (source_id INT, article_id INT, url_extension TEXT UNIQUE, day INT, month INT, year INT)')
    
    article_id = 0

    # iterate through articles from July 2020 to November 2020
    for month in range(7, 12)[:1]:
        
        # iterate over days 1 - 29 of each month
        for day in range(1, 30)[:10]:
            # format url with the dynamic month and day 
            archive_url = "https://www.wsj.com/news/archive/2020/{}/{}".format(str(month), str(day))
            
            try:
                
                # make a request to the archive_url formatted string
                driver.get(archive_url)

                # wait up to 10 seconds for the all of the article URLS to be rendered on the page
                driver.implicitly_wait(10)

                # put all of the articles published on this day into a list
                articles = driver.find_elements_by_tag_name('article')

                # iterate over the first 5 articles
                for article in articles[:5]:
                    
                    # get the url to this specific article
                    url = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')[29:]

                    # THIS IS A DUMMY VALUE
                    # Once the News_Sources table is set up, query that table to figure out what the ID is for the WSJ    
                    source_id = 1

                    cur.execute('INSERT INTO WSJ_URL_Data (source_id, article_id, url_extension, day, month, year) VALUES (?, ?, ?, ?, ?, ?)', (source_id, article_id, url, day, month, 2020))

                    article_id += 1
            except Exception as e:
                print("Error fetching article URLs from {}.\nError message:\n{}\n".format(archive_url, e))
                
            
    # commit the changes to the database
    conn.commit()        

# Creates a second table to store the actual content of each WSJ article.
# Fetches the article_id and url_extension from WSJ_URL_Data table. Uses that 
# url to go to the article's link, scrape the article, and fill a new table in the 
# database which contains the article_id as well as the article_content.
def fillWSJArticleContentTable(cur, conn, driver):
    # source_id (from table above), article_id (from table above), article_content (scraped with selenium)
    
    # create the table w/ the desired columns if it does not exist already
    cur.execute('DROP TABLE IF EXISTS WSJ_Article_Content')
    cur.execute('CREATE TABLE IF NOT EXISTS WSJ_Article_Content (article_id INT, article_content TEXT UNIQUE)')

    cur.execute('SELECT article_id, url_extension FROM WSJ_URL_Data')
    
    # for every row in WSJ_URL_Data, fetch article_id and article_url
    urlTuples = cur.fetchall()

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
            cur.execute('INSERT INTO WSJ_Article_Content (article_id, article_content) VALUES (?, ?)', (article_id, articleContent))
        
        except Exception as e:
            print("Error fetching article content from {}.\nError message:\n{}\n".format(url, e))
    
    # commit the changes to the database
    conn.commit()

# Drives all functions pertaining to the Wall Street Journal.
def wallStreetJournalHandler():
    driver = getChromeDriver("/Users/chasegoldman/Desktop/Michigan/Fall2020/SI206/SI206-FINAL-PROJECT/chromedriver_2", True)
    login_url = "https://accounts.wsj.com/login?target=https%3A%2F%2Fwww.wsj.com%2Fnews%2Farchive%2F2020%2F11%2F27"

    try:
        loginWSJ(driver, login_url, 'gochase@umich.edu', 'SI206Final!')
        cur, conn = setUpDatabase('finalProject.db')
        fillWSJ_URL_Table(cur, conn, driver)
        fillWSJArticleContentTable(cur, conn, driver)
        driver.quit()
    except Exception as e:
        print("Error while handling Wall Street Journal Data.\n Error message:\n{}\n".format(e))
        driver.quit()


wallStreetJournalHandler()



# OLD FUNCTION DEFINITIONS FROM WHEN WE WERE USING CSV FILES


# def getArchiveArticleDictionary(driver):

#     urlDictionary = {}

#     # {date: [headline links for that date]}

#     for month in range(7, 12):
#         for day in range(1, 30):
#             archive_url = "https://www.wsj.com/news/archive/2020/{}/{}".format(str(month), str(day))
            
#             driver.get(archive_url)
#             driver.implicitly_wait(10)

#             date = "{}/{}/2020".format(str(month), str(day))

#             urlDictionary[date] = []
            
#             articles = driver.find_elements_by_tag_name('article')
            
#             for article in articles:
#                 headline = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')
#                 urlDictionary[date].append(headline)
    
#     return urlDictionary


# def writeArchiveDictToFile(archiveArticleDictionary):
#     json_content = json.dumps(archiveArticleDictionary)

#     with open('archiveArticleData.json', 'w') as outfile:
#         outfile.write(json_content)


# def scrapeArticles(driver, login_url, cache_filename, data_filename):
    
#     try:
#         with open(cache_filename, 'r') as infile:
#             with open(data_filename, 'a') as outfile:

#                 outfileWriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#                 # outfileWriter.writerow(["source", "storyContent", "pubDate", 'url'])
                
#                 archiveDictionary = json.loads(infile.read())

#                 for date in list(archiveDictionary.keys())[4:]:
            
#                     urlList = archiveDictionary[date]

#                     for article_url in urlList:
#                         try:
#                             print("Article URL: ", article_url)
#                             driver.get(article_url)
#                             driver.implicitly_wait(15)
#                             articleContent = driver.find_element_by_class_name("article-content  ").text.replace('\n', '')
#                             outfileWriter.writerow(["Wall Stree Journal", articleContent, date, article_url])
#                         except Exception as e:
#                             print("Error occured for this url: ", article_url, '\n')
#                             print(e)
                            
#     except Exception as e:
#         print("An error occured while trying to scrapeArticles.")
#         print(e)


# def main():

#     driver = getChromeDriver("/Users/chasegoldman/Desktop/Michigan/Fall2020/SI206/SI206-FINAL-PROJECT/chromedriver_2", True)

    
#     try:
#         login_url = "https://accounts.wsj.com/login?target=https%3A%2F%2Fwww.wsj.com%2Fnews%2Farchive%2F2020%2F11%2F27"
        
#         # archiveArticleDictionary = getArchiveArticleDictionary(driver)

#         # writeArchiveDictToFile(archiveArticleDictionary)

#         #loginWSJ(driver, login_url, 'gochase@umich.edu', 'SI206Final!')

#         cur, conn = setUpDatabase('finalProject.db')

#         #fillWSJ_URL_Table(cur, conn, driver)

#         fillWSJArticleContentTable(cur, conn, driver)

#         #scrapeArticles(driver, login_url, 'archiveArticleData.json', 'wsj_article_data.csv')

#         driver.quit()
    
#     except Exception as e:
#         print(e)
#         driver.quit()

# if __name__ == "__main__":
#     main()