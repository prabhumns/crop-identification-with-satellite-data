import math

from IPython import display
from matplotlib import cm
from matplotlib import gridspec
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
import tensorflow as tf
from tensorflow.python.data import Dataset

tf.logging.set_verbosity(tf.logging.ERROR)
pd.options.display.max_rows = 10
pd.options.display.float_format = '{:.1f}'.format

print ('starting to read csv')
dataframe = pd.read_csv('entiredata.csv')
print ('read csv')
dataframe = dataframe.reindex(np.random.permutation(dataframe.index))

my_feature = dataframe[['band1', 'band2', 'band3', 'band4']]
feature_columns = [tf.feature_column.numeric_column("band1"), tf.feature_column.numeric_column("band2"), tf.feature_column.numeric_column("band3"), tf.feature_column.numeric_column("band4")]
targets = dataframe['cropname']
my_optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.0000001)
my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 5.0)

linear_classifier = tf.extimator.LinearClassifier(feature_columns = feature_columns, optimizer = my_optimizer)

def my_input_function (features, targets,BufferSize = 1000, batch_size = 1, shuffle = True, num_epochs = None):
    features = {key:np.array(value) for key,value in dict(features).items()}
    ds = Dataset.from_tensor_slices((features, targets))
    ds = ds.batch(batch_size).repeat(num_epochs)
    if shuffle:
        ds = ds.shuffle(buffer_size = BufferSize)
    features, labels = ds.make_one_shot_iterator().get_next()
    return features, labels

linear_classifier.train(input_fn = lambda:my_input_fn(my_feature, targets, batch_size))

pridictions_input_fn = lambda: my_input_function(my_feature, targets, num_epochs = 1)
predictions = linear_classifier.predict(input_fn = prediction_input_fn)
mean_squared_error = metrics.mean_squared_error(targets, predictions)
print (math.sqrt(mean_squared_error))