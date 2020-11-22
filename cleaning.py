import pandas as pd
import csv
import os

fake_path = os.path.abspath('../Fake.csv')
print(fake_path)

# load in data from fake and true datasets 
fake = pd.read_csv(fake_path)
#true = pd.read_csv("True.csv")