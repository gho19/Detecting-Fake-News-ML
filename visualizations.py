import unittest
import sqlite3
import os
import plotly.graph_objects as go
import pandas as pd

# FILE FOR MAKING CALCULATIONS

# NYT_ArticleContent
# NYT_Sections
# NYT_URL_Data
# News_API
# Sources (calculation 1)
# Twitter
# Twitter_users
# WSJ_Article_Content
# WSJ_URL_Data

# You must select some data from all of the tables in your database and calculate something from that data
# You must do at least one database join to select your data
# Write out the calculated data to a file as text

# STEP 0:
    # make the table we talked about earlier
    # source_id, article_id, classified as real or fake, expected real or fake

# 1. For each source in the sources table, calculate the number of articles we have for that source


# 2. Machine learning - for each article that we have in the database, is it predicted to be real or fake news?
    # combine the Twitter

# 3. 

# Connects to database to pull data from tables in database 
# Has db_name as a parameter, a string, for the database file name
# returns cur and conn 
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# Compiles data from the 'Calculation_Table' into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationData(cur, conn):
    cur.execute('SELECT ml_classification FROM Calculation_Table')
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie
# Compiles data from the 'Calculation_Table' where source is from Twitter into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationTwitterData(cur, conn):
    cur.execute('SELECT source_id FROM Sources WHERE source_name = "Twitter"')
    source_id = cur.fetchone()[0]
    cur.execute('SELECT ml_classification FROM Calculation_Table WHERE source_id = "{}"'.format(source_id))
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie

# Compiles data from the 'Calculation_Table' where source is from NYT into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationNYTData(cur, conn):
    cur.execute('SELECT source_id FROM Sources WHERE source_name = "The New York Times"')
    source_id = cur.fetchone()[0]
    cur.execute('SELECT ml_classification FROM Calculation_Table WHERE source_id = "{}"'.format(source_id))
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie

# Compiles data from the 'Calculation_Table' where source is from WSJ into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationWSJData(cur, conn):
    cur.execute('SELECT source_id FROM Sources WHERE source_name = "The Wall Street Journal"')
    source_id = cur.fetchone()[0]
    cur.execute('SELECT ml_classification FROM Calculation_Table WHERE source_id = "{}"'.format(source_id))
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie

# Utilizing the plotly library, this function creates a pie chart
# with the percentage of Fake News and True News
# Takes a dictionary as a paramater
def visualizations(dictionary):
    labels = list(dictionary.keys())    
    values = list(dictionary.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.show()



cur, conn = setUpDatabase('finalProject.db')

all_data = mlClassificationData(cur, conn)
visualizations(all_data)

twitter_data = mlClassificationTwitterData(cur, conn)
visualizations(twitter_data)

nyt_data = mlClassificationNYTData(cur, conn)
visualizations(nyt_data)

wsj_data = mlClassificationWSJData(cur, conn)
visualizations(wsj_data)