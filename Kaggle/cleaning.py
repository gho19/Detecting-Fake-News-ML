import pandas as pd
import csv
import os

### THIS CLEANING SCRIPT WAS TAKEN FROM: https://enlight.nyc/projects/build-a-naive-bayes-classifier

fake_path = os.path.abspath('../Fake.csv')
print(fake_path)

# load in data from fake and true datasets 
fake = pd.read_csv('fake.csv')
true = pd.read_csv('true.csv')

# Set True News column to 0 
# Set Fake News column to 1
true['fake_news'] = 0 
fake['fake_news'] = 1

only_text = true['text']

only_text = only_text.str.extractall(r'^.* - (?P<text>.*)')

only_text = only_text.droplevel(1)

true = true.assign(text = only_text['text'])

# Combine Fake and True datasets
df = pd.concat([fake, true], axis = 0)

# Drop date, title, and subject column
df = df.drop(['subject', 'date', 'title'], axis = 1)

# Drop N/A cells 
df = df.dropna(axis = 0) 

# Export Cleaned News Dataset
clean_text = df.to_csv('cleaned_news.csv', index = False)