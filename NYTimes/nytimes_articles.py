import requests
import json
from bs4 import BeautifulSoup as bs
import csv
import time
import random

# This script opens the file with all of the New York Times article URLS. Then, for each
# URL, it checks if it is from a section of the newspaper that we care about, and if it is
# then it scrapes the text content of that article and writes it to a CSV file.


with open('nytimes_urls.csv', 'r') as infile:
    with open('nytimes_article_data.csv', 'w') as outfile:
        
        outfileWriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        outfileWriter.writerow(["source", "storyContent", "pubDate", "sectionName", 'url', 'wordCount', 'printPage'])
        
        good_section_names = ['U.S.', 'World', 'Education', 'Science', 'Today’s Paper', 'New York', 'Health', 'The Upshot', 'Politics']

        rows = infile.readlines()
        
        for row in rows[1:]:
            cells = row.split(',')

            sectionName = cells[3]

            if sectionName in good_section_names:

                time.sleep(random.random())

                source = cells[0]
                url = cells[1]
                pubDate = cells[2]
                wordCount = cells[4]
                printPage = cells[5].strip()

                try:
                    resp = requests.get(url)
                    soup = bs(resp.text, 'html.parser')
                    story_content = soup.find('section', {'name':"articleBody"}).text.replace('\n', '')
                    outfileWriter.writerow([source, story_content, pubDate, sectionName, url, wordCount, printPage])
                except:
                    print("got an exception")
                    continue




