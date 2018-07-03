import pickle
from random import shuffle
import numpy as np
from statistics import mean
import nn1

def find_accuracy(lis1, lis2):
	n = 0
	for i in range(len(lis2)):
		if lis1[i] == lis2[i]:
			n = n+1
	return float(n/len(lis2))

file_object = open('data_collect4.pkl','rb')
dicti = pickle.load(file_object)
file_object.close()
data2 =  dicti['data']
data = data2
data = {key:value[:11000] for key, value in data.items() if len(value)>=11000}

data = {key: [[np.uint16(i) for key2 in ['07','08','09','10','11','12']  for i in list(example[key2])] for example in value] for key, value in data.items()}

for i in range(30):
	lin = []
	for key, value in data.items():
		if key!= 'info':
			for l in value:
				lin.append(l[i])
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
i = 0;
for key, value in data.items():
	if i <2:
		training_examples = training_examples + value[:9000]
		cv_examples = cv_examples + value[9000:10000]
		test_examples = test_examples + value[10000:]
		training_labels = training_labels + [i for v in range(9000)]
		cv_labels = cv_labels + [i for v in range(1000)]
		test_labels = test_labels + [i for v in range(1000)]
		print(i,':', key)
		i+=1

layer_details = {0:30,1:10,2:5,3:3,4:1}

parameters = nn1.neur_net(layer_details = layer_details, 
				steps = 5000, 
				training_examples = training_examples, 
				training_labels = training_labels, 
				batch_size = 500, 
				learning_rate = 0.001,
				 activation_function = 'relu')

predictions1 = nn1.predict(parameters = parameters, 
				layer_details = layer_details,
				test_example = cv_examples)

predictions2 = nn1.predict(parameters = parameters, 
				layer_details = layer_details,
				test_example = training_examples)

acc = find_accuracy(predictions1, cv_labels)
loss = find_accuracy(predictions2, training_labels)

print("acc = ", acc)
print("loss = ", loss)

parameters = nn1.neur_net(layer_details = layer_details, 
				steps = 5000, 
				training_examples = training_examples, 
				training_labels = training_labels, 
				batch_size = 500, 
				learning_rate = 0.001,
				 activation_function = 'tanh')

predictions1 = nn1.predict(parameters = parameters, 
				layer_details = layer_details,
				test_example = cv_examples)

predictions2 = nn1.predict(parameters = parameters, 
				layer_details = layer_details,
				test_example = training_examples)

acc = find_accuracy(predictions1, cv_labels)
loss = find_accuracy(predictions2, training_labels)

print("acc = ", acc)
print("loss = ", loss)

parameters = nn1.neur_net(layer_details = layer_details, 
				steps = 5000, 
				training_examples = training_examples, 
				training_labels = training_labels, 
				batch_size = 500, 
				learning_rate = 0.001,
				 activation_function = 'lrelu')

predictions1 = nn1.predict(parameters = parameters, 
				layer_details = layer_details,
				test_example = cv_examples)

predictions2 = nn1.predict(parameters = parameters, 
				layer_details = layer_details,
				test_example = training_examples)

acc = find_accuracy(predictions1, cv_labels)
loss = find_accuracy(predictions2, training_labels)

print("acc = ", acc)
print("loss = ", loss)