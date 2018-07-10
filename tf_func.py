import tensorflow as tf
import time

def nn_model_fn(features, labels, mode):
	regularizer = tf.contrib.layers.l2_regularizer(scale = 0.0000001)
	input_layer = tf.reshape(features["x"], [-1,45])

	dense1 = tf.layers.dense(
				inputs=input_layer, 
				units= 500, #number of neurons 
				activation=tf.nn.leaky_relu,
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
				units= 500, #number of neurons 
				activation=tf.nn.leaky_relu,
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
				units= 500, #number of neurons 
				activation=tf.nn.leaky_relu,
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
				units= 100, #number of neurons 
				activation=tf.nn.leaky_relu,
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
				units= 6, #number of neurons 
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
		optimizer = tf.train.AdadeltaOptimizer(use_locking=True)
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


def tf_training(training_examples, training_labels):
	tf.logging.set_verbosity(tf.logging.INFO)
	my_classifier = tf.estimator.Estimator(
		model_fn=nn_model_fn, model_dir="E:/crop_identification_with_satellite_data/crop_identification_with_satellite_data/tf_files") #Use this directory
	
	tensors_to_log = {"probabilities": "softmax_tensor"}
	
	logging_hook = tf.train.LoggingTensorHook(
				tensors=tensors_to_log, every_n_iter=1000)
	
	training_input_fn = tf.estimator.inputs.numpy_input_fn(
				x={"x": training_examples},
				y=training_labels,
				batch_size=10000,
				num_epochs=None,   
				shuffle=True)
				 #input function takes our data and gives whenever asked
	my_classifier.train(
				input_fn=training_input_fn,
				steps=200000,
				hooks=[logging_hook])
	
	cv_input_fn = tf.estimator.inputs.numpy_input_fn(
				x={"x": training_examples},
				y= training_labels,
				num_epochs=1,
				shuffle=False)

	eval_results = my_classifier.evaluate(input_fn=cv_input_fn)

	print(eval_results)
