import unittest
import sqlite3
import json
import os
import ml

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# TRAINING OUR MODEL
df = pd.read_csv('cleaned_kaggle_news.csv')

# Split the data
DV = 'fake_news' # The dependent variable, text is the independent variable here

X = df.drop([DV], axis = 1) # Drop from our X array because this is the text data that gets trained
y = df[DV]

# Training on 75% of the data, test on the rest
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.25)

count_vect = CountVectorizer(max_features = 10000) # limiting to 5000, but room to play with this here!
X_train_counts = count_vect.fit_transform(X_train['text']) 
# print(count_vect.vocabulary_) # here is our bag of words! 
X_test = count_vect.transform(X_test['text']) # note: we don't fit it to the model! Or else this is all useless


# Fit the training dataset on the NB classifier
Naive = MultinomialNB()
Naive.fit(X_train_counts, y_train)


# Predict the labels on validation dataset
predictions_NB = Naive.predict(X_test)

def classifier(text):
    Naive = MultinomialNB()
    Naive.fit(X_train_counts, y_train)
    
    word_vec = count_vect.transform(text) 
    
    predict = Naive.predict(word_vec)
    return 0 if predict[0] else 1

# Connects this file to the database
# setUpDataBase() takes db_name, a string, as a parameter 
# creating a database with db_name
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# Retrieves the source ID from the 'Sources' table in the database and 
# checks if Source exists in table already 
# setSourceID() takes curr + conn (for connecting to database) 
# and source_name, a string, the name of a table in a database
# returns the source_id associated with that source
def getSourceID(cur, conn, source_name):

    cur.execute('CREATE TABLE IF NOT EXISTS Sources (source_id INT, source_name TEXT)')
    
    cur.execute('SELECT source_id, source_name FROM Sources')
    
    id_name_tups = cur.fetchall()
    source_ids = [tup[0] for tup in id_name_tups]
    source_names = [tup[1] for tup in id_name_tups]

    # if we already have this source in the sources_table
    if source_name in source_names:
        cur.execute('SELECT source_id FROM Sources WHERE Sources.source_name = "{}"'.format(source_name))
        source_id = cur.fetchone()[0]
        
    # if we don't already have this source in the sources table
    else:
        highest_id = getHighestId(cur, conn, 'source_id', 'Sources')
        cur.execute('INSERT INTO Sources (source_id, source_name) VALUES (?,?)', (highest_id, source_name))
        source_id = highest_id
    
    conn.commit()
    return source_id

# Retrieves the highest ID for a respective table to ensure ID is unique
# getHighestID() takes curr + conn (for connecting to database) as a parameter
# and takes column_name, a string, (of a table) and table_name, a string 
# returns the highest ID for a column
def getHighestId(cur, conn, column_name, table_name):
    cur.execute('SELECT {} FROM {}'.format(column_name, table_name))
    
    section_id_list = [int(tup[0]) for tup in cur.fetchall()]

    if section_id_list != []: 
        highest_id = max(section_id_list) + 1
    
    else:
        highest_id = 0
    
    conn.commit()
    return highest_id

# Creates 'Calculation_Table'
# Grabs source_id, article/tweet_id, and content from columns in NYT, Twitter, New API, and WSJ table
# Inputs data into the 'Calculation_Table' from tables and machine learning calculation based on content
# takes curr + conn (for connecting to database) as a parameter
# The columns in the table are as follows: source_id, article_id, ml_classification
def compileCalculationTable(cur, conn):
    cur.execute('DROP TABLE IF EXISTS Calculation_Table')

    # source_id, article_id, classified as real or fake, expected real or fake
    cur.execute('CREATE TABLE IF NOT EXISTS Calculation_Table (source_id INT, article_id INT, ml_classification INT)')

    # Retrieves Source ID, Article/Tweet ID, and Content of Article/Tweet from respective tables
    cur.execute('SELECT source_id, article_id, article_content FROM NYT_ArticleContent')
    nyt_article_tuples = cur.fetchall()

    cur.execute('SELECT SourceId, ArticleId, Title FROM News_API')
    news_api_article_tuples = cur.fetchall()

    cur.execute('SELECT SourceId, TweetId, Tweet FROM Twitter')
    twitter_article_tuples = cur.fetchall()

    cur.execute('SELECT source_id, article_id, article_content FROM WSJ_Article_Content')
    wsj_article_tuples = cur.fetchall()

    # Creates tuple of all data gathered 
    all_source_tuples = nyt_article_tuples + news_api_article_tuples + twitter_article_tuples + wsj_article_tuples
    
    # Loops through tuples 
    for tup in all_source_tuples:
        source_id = tup[0]
        article_id = tup[1]
        article_content = tup[2]

        # MACHINE LEARNING CALCULATION
        ml_classification = ml.classifier([article_content])

        cur.execute('INSERT INTO Calculation_Table (source_id, article_id, ml_classification) VALUES (?,?,?)', (tup[0], tup[1], ml_classification))

    conn.commit()

# Connects to finalProject.db and inserts data into 'Calculation_Table' table  
def main():
    cur, conn = setUpDatabase('finalProject.db')
    compileCalculationTable(cur, conn)
    conn.close()


if __name__ == "__main__":
    main()