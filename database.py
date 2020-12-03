import unittest
import sqlite3
import json
import os
from WSJ import wsj as wallstreet
from NYTimes import *


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
