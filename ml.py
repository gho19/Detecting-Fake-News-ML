import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

df = pd.read_csv('cleaned_kaggle_news.csv')

# Split the data
DV = 'fake_news' # The dependent variable, text is the independent variable here

X = df.drop([DV], axis = 1) # Drop from our X array because this is the text data that gets trained
y = df[DV]

# Training on 75% of the data, test on the rest
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.25)

count_vect = CountVectorizer(max_features = 10000)# limiting to 5000, but room to play with this here!
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


def classifier(text):
    Naive = MultinomialNB()
    Naive.fit(X_train_counts, y_train)
    
    # n.b: you may need to wrap the argument in brackets to make it a vector if you passed in a string
    word_vec = count_vect.transform(text) 
    
    predict = Naive.predict(word_vec)
    return "Fake News" if predict[0] else "True News"

























