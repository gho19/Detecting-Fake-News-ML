import requests
import pandas as pd

# API Key: 61e924b119ab4e4294956f2da5d1d01c

url = ('http://newsapi.org/v2/top-headlines?country=us&apiKey=61e924b119ab4e4294956f2da5d1d01c')
response = requests.get(url)
data = response.json()

entries = []

for news in data['articles']:
    title = news['title'].split(' - ')
    source = news['source']['name']
    entries.append([source, title[0], news['description'], news['publishedAt']])

news_df = pd.DataFrame(entries, columns = ['source', 'title', 'storyContent', 'pubDate'])
news_df.to_csv('news_api.csv', index = False)






