import unittest
import sqlite3
import json
import os

# OFFICE HOURS QUESTIONS:
# 1. Is it considered duplicate data if two articles contain the same word? If so, how should we deal with this? Should we create
# another table which assigns every single word in the entire database an integer value and then have our article text cells just be
# strings of integers seperated by spaces?
# 2. Is it okay to use our CSV files to then pull data from those into the database, or do we have to delete those CSV files and
# put data immediately into the database when we have pulled it from the web?
# 3. How can we implement something for the 25 Items per Execution rule? What would that look like in terms of actual code?
# 4. What do we do about the fact that our database is way too large to go on github? How are we supposed to fill it properly?

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
            for i, row in enumerate(rows[1:]):
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
