import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# THIS ML ALGORITHM WAS TAKEN FROM: https://enlight.nyc/projects/build-a-naive-bayes-classifier

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

# Use accuracy_score function to get the accuracy
print('Accuracy Score:', accuracy_score(predictions_NB, y_test) * 100)

# classifier() takes text, a list of strings, as a parameter 
# This function classifies text as 'Fake News' or 'True News' 
def classifier(text):
    Naive = MultinomialNB()
    Naive.fit(X_train_counts, y_train)
    
    word_vec = count_vect.transform(text) 
    
    predict = Naive.predict(word_vec)
    return "Fake News" if predict[0] else "True News"


lst_strings = ['''

Mario M. Cuomo, the three-term governor of New York who commanded the attention of the country with a compelling public presence, a forceful defense of liberalism and his exhaustive ruminations about whether to run for president, died on Thursday at his home in Manhattan. He was 82.His family confirmed the death, which occurred only hours after Mr. Cuomo’s son Andrew M. Cuomo was inaugurated in Manhattan for a second term as governor. The cause was heart failure.Mario Cuomo led New York during a turbulent time, 1983 through 1994. His ambitions for an activist government were thwarted by recession. He found himself struggling with the State Legislature not over what the government should do but over what programs should be cut, and what taxes should be raised, simply to balance the budget.Still, no matter the problems he found in Albany, Mr. Cuomo burst beyond the state’s boundaries to personify the liberal wing of his national party and become a source of unending fascination and, ultimately, frustration for Democrats, whose leaders twice pressed him to run for president, in 1988 and 1992, to no avail.In an era when liberal thought was increasingly discredited, 
Mr. Cuomo, a man of large intellect and often unrestrained personality, celebrated it, 
challenging Ronald Reagan at the height of his presidency with an expansive and affirmative 
'''
]

print(classifier(lst_strings))

















