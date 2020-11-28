import requests
import json
from bs4 import BeautifulSoup as bs
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options





def getChromeDriver(path, headless = False):
    
    if headless:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=path, options=chrome_options)
    else:
        driver = webdriver.Chrome(executable_path=path)
    
    return driver


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

    
    
def getArchiveArticleDictionary(driver):

    urlDictionary = {}

    # {date: [headline links for that date]}

    for month in range(7, 12):
        for day in range(1, 30):
            archive_url = "https://www.wsj.com/news/archive/2020/{}/{}".format(str(month), str(day))
            
            driver.get(archive_url)
            driver.implicitly_wait(10)

            date = "{}/{}/2020".format(str(month), str(day))

            urlDictionary[date] = []
            
            articles = driver.find_elements_by_tag_name('article')
            
            for article in articles:
                headline = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')
                urlDictionary[date].append(headline)
    
    return urlDictionary


def writeArchiveDictToFile(archiveArticleDictionary):
    json_content = json.dumps(archiveArticleDictionary)

    with open('archiveArticleData.json', 'w') as outfile:
        outfile.write(json_content)


def scrapeArticles(driver, login_url, cache_filename, data_filename):
    
    try:
        with open(cache_filename, 'r') as infile:
            with open(data_filename, 'a') as outfile:

                outfileWriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                # outfileWriter.writerow(["source", "storyContent", "pubDate", 'url'])
                
                archiveDictionary = json.loads(infile.read())

                for date in list(archiveDictionary.keys())[4:]:
            
                    urlList = archiveDictionary[date]

                    for article_url in urlList:
                        try:
                            print("Article URL: ", article_url)
                            driver.get(article_url)
                            driver.implicitly_wait(15)
                            articleContent = driver.find_element_by_class_name("article-content  ").text.replace('\n', '')
                            outfileWriter.writerow(["Wall Stree Journal", articleContent, date, article_url])
                        except Exception as e:
                            print("Error occured for this url: ", article_url, '\n')
                            print(e)
                            
    except Exception as e:
        print("An error occured while trying to scrapeArticles.")
        print(e)





def main():

    driver = getChromeDriver("/Users/chasegoldman/Desktop/Michigan/Fall2020/SI206/SI206-FINAL-PROJECT/chromedriver_2", True)

    
    try:
        login_url = "https://accounts.wsj.com/login?target=https%3A%2F%2Fwww.wsj.com%2Fnews%2Farchive%2F2020%2F11%2F27"
        
        # archiveArticleDictionary = getArchiveArticleDictionary(driver)

        # writeArchiveDictToFile(archiveArticleDictionary)

        loginWSJ(driver, login_url, 'gochase@umich.edu', 'SI206Final!')

        scrapeArticles(driver, login_url, 'archiveArticleData.json', 'wsj_article_data.csv')

        driver.quit()
    
    except Exception as e:
        print(e)
        driver.quit()

if __name__ == "__main__":
    main()
    