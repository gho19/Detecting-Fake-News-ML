import unittest
import sqlite3
import json
import os

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
# cut down on the data
# OR
# you can compress the data in the database 
# https://docs.github.com/en/free-pro-team@latest/github/managing-large-files/working-with-large-files


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def setUpKaggleTable(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Kaggle")
    cur.execute("CREATE TABLE Kaggle (story_text TEXT, real_news INT)")

    conn.commit()

def fillKaggleTable(kaggle_csv_filename, cur, conn):
    setUpKaggleTable(cur, conn)
    path = os.path.dirname(os.path.abspath(__file__)) + '/Kaggle/' + kaggle_csv_filename
    try:
        with open(path, 'r') as infile:
            rows = infile.readlines()
            for row in rows[1:]:
                story_text = row[:-3]
                real_news_indicator = row.split(',')[-1]
                cur.execute("INSERT INTO Kaggle (story_text,real_news) VALUES (?,?)",(story_text, real_news_indicator))
        conn.commit()
    except:
        print("Unable to open {}. Please try again.".format(kaggle_csv_filename))








def main():
    cur, conn = setUpDatabase('finalProject.db')
    fillKaggleTable('cleaned_kaggle_news.csv', cur, conn)
    conn.close()


if __name__ == "__main__":
    main()
