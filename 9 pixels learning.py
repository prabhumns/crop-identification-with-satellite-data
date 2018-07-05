import pickle
from statistics import mean
from random import shuffle
import numpy as np
from sklearn.utils import shuffle as shf
import tensorflow as tf
import time

tf.logging.set_verbosity(tf.logging.INFO)
regularizer = tf.contrib.layers.l2_regularizer(scale = 0.1)
print(regularizer)

def nn_model_fn(features, labels, mode):
	input_layer = tf.reshape(features["x"], [-1,45])

	dense1 = tf.layers.dense(
				inputs=input_layer, 
				units= 30, #number of neurons 
				activation=tf.nn.relu,
				use_bias= True,
				kernel_initializer=None, #initial weight available if any
				bias_initializer= None, #similar to previous
				kernel_regularizer= regularizer, #different degularisation for each layer
				bias_regularizer= None, 
				activity_regularizer= None,
				kernel_constraint = None,
				bias_constraint= None,
				trainable= True,
				name = None,
				reuse = None
				)

	dense2 = tf.layers.dense(
				inputs=dense1, 
				units= 30, #number of neurons 
				activation=tf.nn.relu,
				use_bias= True,
				kernel_initializer=None, #initial weight available if any
				bias_initializer= None, #similar to previous
				kernel_regularizer= regularizer, #different degularisation for each layer
				bias_regularizer= None, 
				activity_regularizer= None,
				kernel_constraint = None,
				bias_constraint= None,
				trainable= True,
				name = None,
				reuse = None
				)

	dense3 = tf.layers.dense(
				inputs=dense2, 
				units= 10, #number of neurons 
				activation=tf.nn.relu,
				use_bias= True,
				kernel_initializer=None, #initial weight available if any
				bias_initializer= None, #similar to previous
				kernel_regularizer= regularizer, #different degularisation for each layer
				bias_regularizer= None, 
				activity_regularizer= None,
				kernel_constraint = None,
				bias_constraint= None,
				trainable= True,
				name = None,
				reuse = None
				)

	dense4 = tf.layers.dense(
				inputs=dense3, 
				units= 10, #number of neurons 
				activation=tf.nn.relu,
				use_bias= True,
				kernel_initializer=None, #initial weight available if any
				bias_initializer= None, #similar to previous
				kernel_regularizer= regularizer, #different degularisation for each layer
				bias_regularizer= None, 
				activity_regularizer= None,
				kernel_constraint = None,
				bias_constraint= None,
				trainable= True,
				name = None,
				reuse = None
				)
	
	logits = tf.layers.dense(
				inputs=dense4, 
				units=5, #number of neurons 
				activation= None,
				use_bias= True,
				kernel_initializer=None, #initial weight available if any
				bias_initializer= None, #similar to previous
				kernel_regularizer= regularizer, #different degularisation for each layer
				bias_regularizer= None, 
				activity_regularizer= None,
				kernel_constraint = None,
				bias_constraint= None,
				trainable= True,
				name = None,
				reuse = None
				)

	predictions = {
				"classes": tf.argmax(input=logits, axis=1),
				"probabilities": tf.nn.softmax(logits, name="softmax_tensor") #it applies softmax to the value given by logits
				}

	if mode == tf.estimator.ModeKeys.PREDICT:
		return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)
	
	loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits) #make sure that the activation for logits is none

  # Configure the Training Op (for TRAIN mode)
	if mode == tf.estimator.ModeKeys.TRAIN:
		optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.00001, use_locking=True)
		t = time.time()
		train_op = optimizer.minimize(
			loss=loss, #this is just dataloss, not with regularization term. correction for regularisation happens along with training
			global_step=tf.train.get_global_step())
		print('time: ', time.time() - t)
		return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

	eval_metric_ops = {
		"accuracy": tf.metrics.accuracy(
			labels=labels, predictions=predictions["classes"])}
	return tf.estimator.EstimatorSpec(
		mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

if __name__ == '__main__':
	file_object = open('E:/Time Series/pra.pkl', 'rb')
	data2 = pickle.load(file_object)
	file_object.close()
	data = data2['data']

	data = {key:value[:6000] for key, value in data.items() if len(value) >= 6000}

	mins = {}; maxs = {}; means = {}
	for i in range(45):
		lin = [l[i] for value in data.values() for l in value]
		mins[i] = min(lin)
		maxs[i] = max(lin)
		means[i] = mean(lin)
	
	data = {key: [[np.float64((example[i]-means[i])/(maxs[i] - mins[i])) for i in range(45)] for example in value] for key, value in data.items()}	

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
	
	training_examples = np.array(training_examples)
	training_labels = np.array(training_labels)
	cv_examples = np.array(cv_examples)
	cv_labels = np.array(cv_labels)
	test_examples = np.array(test_examples)
	test_labels = np.array(test_labels)


	my_classifier = tf.estimator.Estimator(
		model_fn=nn_model_fn, model_dir="E:/crop_identification_with_satellite_data/crop_identification_with_satellite_data/tf_files") #Use this directory
	
	tensors_to_log = {"probabilities": "softmax_tensor"}
	
	logging_hook = tf.train.LoggingTensorHook(
				tensors=tensors_to_log, every_n_iter=1000)
	
	training_input_fn = tf.estimator.inputs.numpy_input_fn(
				x={"x": training_examples},
				y=training_labels,
				batch_size=100,
				num_epochs=None,   
				shuffle=True)
				 #input function takes our data and gives whenever asked
	my_classifier.train(
				input_fn=training_input_fn,
				steps=200000,
				hooks=[logging_hook])
	
	cv_input_fn = tf.estimator.inputs.numpy_input_fn(
				x={"x": cv_examples},
				y= cv_labels,
				num_epochs=1,
				shuffle=False)

	eval_results = my_classifier.evaluate(input_fn=cv_input_fn)

	print(eval_results)
