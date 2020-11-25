import unittest
import sqlite3
import json
import os


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
    unittest.main(verbosity = 2)