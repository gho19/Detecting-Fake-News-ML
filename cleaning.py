import pandas as pd

def open_file(filename):
    self.root_path = os.path.dirname(os.path.abspath(__file__))
    self.filepath = os.path.join(self.root_path, filepath)
    self.file_obj = open(self.filepath, 'r', errors = 'replace')
    

# load in data from fake and true datasets 
fake = pd.read_csv("Fake.csv")
true = pd.read_csv("True.csv")