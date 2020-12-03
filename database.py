import unittest
import sqlite3
import json
import os
from WSJ import wsj as wallstreet
from NYTimes import *


#from NYTimes import nytimes_urls, nytimes_articles


# OFFICE HOURS QUESTIONS:
# 1. Is it considered duplicate data if two articles contain the same word? If so, how should we deal with this? Should we create
# another table which assigns every single word in the entire database an integer value and then have our article text cells just be
# strings of integers seperated by spaces?
# this is not considered duplicated data 

# 2. Is it okay to use our CSV files to then pull data from those into the database, or do we have to delete those CSV files and
# put data immediately into the database when we have pulled it from the web?
# directly put this into the database

# 3. How can we implement something for the 25 Items per Execution rule? What would that look like in terms of actual code?
# need to demonstrate that you know how to deal with putting data into the db in chunks instead of all at once
# for the first 100 items, grab 25 items 4 times, after the first 100 items you can put them into the db all in one go

# 4. What do we do about the fact that our database is way too large to go on github? How are we supposed to fill it properly?
# cut down on the data (I think this is the best option for us bc the results don't really matter that much)
# OR
# you can compress the data in the database 
# https://docs.github.com/en/free-pro-team@latest/github/managing-large-files/working-with-large-files

# keep the kaggle data as CSV files

# Ideas for reformatting the code:
# This file, database.py, can have only functions that set up the database and set up each table inside of the database
# Then, in the other files where we are running scripts that have info that needs to get inserted into the db, we can simply scrape
# the info and then insert it directly into the corresponding table in the database
# We really should put the kaggle data into the database as well just so everything is in the database

# action steps
# fill in all of the functions below

# start changing the web scraping / API scripts to go directly into the database tables instead of CSV files


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn



# def main():
#     cur, conn = setUpDatabase('finalProject.db')
#     conn.close()


# if __name__ == "__main__":
#     main()
