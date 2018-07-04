import pickle
from statistics import mean
from random import shuffle
import numpy as np
from sklearn.utils import shuffle as shf

file_object = open('E:/Time Series/pra.pkl', 'rb')
data = pickle.load(file_object)
file_object.close()

data = {key:value[:6000] for key, value in data.items() if len(value) >= 6000}

for i in range(45):
    lin = [l[i] for value in data.values() for l in value]
    mins = min(lin)
    maxs = max(lin)
    means = mean(lin)
    for key, value in data.items():
        for example in value:
            example[i] = np.float64((example[i] - means)/(maxs-mins))

training_examples = []
training_labels = []
test_examples = []
test_labels = []
cv_examples = []
cv_labels = []
i = 0
for key, value in data.items():
    training_examples = training_examples + value[:5000]
    cv_examples = cv_examples + value[5000:5500]
    test_examples = test_examples + value[5500:]
    training_labels = training_labels + [i for v in range(5000)]
    cv_labels = cv_labels + [i for v in range(500)]
    test_labels = test_labels + [i for v in range(500)]
    print(i,':', key)
    i+=1


