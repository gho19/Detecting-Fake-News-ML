import requests
import json
from bs4 import BeautifulSoup as bs
import csv
import time
import os


# going to need this function at the top of all our files that insert data into the database
# make sure that the path to the database is correct
 
def connectToDB(db_name):
    path = os.path.dirname(os.path.abspath(__file__)).replace("/NYTimes", '')
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

connectToDB('finalProject.db')

# This script is collecting the URLS for all articles published by the New York Times
# in 2015 and 2016 (before Trump and the first year of Trump). 
# Then, there will be another script that scrapes the text content from each article URL and
# puts that text content into the database

# API_KEY = "JdfhwcfpxaR5uHaqRSpZMSxuxsA78twm"

# with open('nytimes_urls.csv', 'w') as outfile:
#     outfileWriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     outfileWriter.writerow(["source", "url", "pubDate", "sectionName", 'wordCount', 'printPage'])
    
#     for year in range(2015, 2017):
#         for month in range(1, 13, 2):
            
#             time.sleep(1)

#             base_url = "https://api.nytimes.com/svc/archive/v1/{}/{}.json?api-key={}".format(str(year), str(month), API_KEY)
#             resp = requests.get(base_url)
#             data_dict = json.loads(resp.text)

            
#             for mini_dict in data_dict["response"]["docs"]:
#                 try:
#                     url = mini_dict["web_url"]
#                     pub_date = mini_dict['pub_date']
#                     section_name = mini_dict['section_name']
#                     wordCount = str(mini_dict['word_count'])
#                     printPage = mini_dict['print_page']
#                     # write this into a table in the database instead

#                     # outfileWriter.writerow(['New York Times', url, pub_date, section_name, wordCount, printPage])
#                 except:
#                     continue





