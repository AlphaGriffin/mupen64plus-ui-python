#!/usr/bin/env python
""" Mupen64 TF-DataPrep
Process the FilePath of Npz to Model, Model to Model, Model to Print

Alphagriffin.com
Eric Petersen @Ruckusist <eric.alphagriffin@gmail.com>
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'
import tensorflow as tf
import numpy as np
# from tqdm import tqdm

__author__ = "Eric Petersen @Ruckusist"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.1"
__maintainer__ = "Eric Petersen"
__email__ = "ruckusist@alphagriffin.com"
__status__ = "Prototype"

"""
# Data Stuffs!!
dataset_paths = "/pub/dataset/mario/"
# input_filename = 'super_set.npz'
input_filename = 'mariokart64_dataset_0.npz'
input_files = os.path.join(dataset_paths, input_filename)
load = np.load(input_files)
imgs = load['images']
labels = load['labels']
dataset_examples = imgs.shape[0]
dataset_h = imgs.shape[1]
dataset_w = imgs.shape[2]
dataset_c = imgs.shape[3]
dataset_classes = labels.shape[1]
dataset_shape = imgs[0].shape
label_example = labels[0]
IMG_W = dataset_w
IMG_H = dataset_h
OUT_SHAPE = dataset_classes
print("Images: {}".format(imgs.shape))
print("Labels: {}".format(labels.shape))
print("Image shape: {}".format(dataset_shape))
print("Label: {}".format(label_example))

# Data Output Stuffs!!
#save_path = '/pub/models/mupen64/mariokart64/'
#save_dirname = 'outputmodel__/alphagriffin'
#save_path = os.path.join(save_path, save_dirname)
save_path = '/tmp/savestuff'
print(save_path)
"""

IMG_W = 200
IMG_H = 66
OUT_SHAPE = 5

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W, stride):
    return tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding='VALID')


x = tf.placeholder(tf.float32, shape=[None, IMG_H, IMG_W, 3])
y_ = tf.placeholder(tf.float32, shape=[None, OUT_SHAPE])
x_image = x
tf.add_to_collection('x_image',x_image)
tf.add_to_collection('y_', y_)

W_conv1 = weight_variable([5, 5, 3, 16])
b_conv1 = bias_variable([16])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1, 2) + b_conv1)

#second convolutional layer
W_conv2 = weight_variable([5, 5, 16, 36])
b_conv2 = bias_variable([36])
h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2, 2) + b_conv2)

#third convolutional layer
W_conv3 = weight_variable([5, 5, 36, 48])
b_conv3 = bias_variable([48])
h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3, 2) + b_conv3)

#fourth convolutional layer
W_conv4 = weight_variable([3, 3, 48, 64])
b_conv4 = bias_variable([64])
h_conv4 = tf.nn.relu(conv2d(h_conv3, W_conv4, 1) + b_conv4)

#fifth convolutional layer
W_conv5 = weight_variable([3, 3, 64, 64])
b_conv5 = bias_variable([64])
h_conv5 = tf.nn.relu(conv2d(h_conv4, W_conv5, 1) + b_conv5)

# Flatten Layer
h_conv5_flat = tf.reshape(h_conv5, [-1, 1152])

#FCL 1
W_fc1 = weight_variable([1152, 1164])
b_fc1 = bias_variable([1164])
h_fc1 = tf.nn.relu(tf.matmul(h_conv5_flat, W_fc1) + b_fc1)

# Start Adding a Dropout for awesomeness .8 is given but mess with it
keep_prob = tf.placeholder(tf.float32)
tf.add_to_collection('keep_prob', keep_prob)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

#FCL 2
W_fc2 = weight_variable([1164, 100])
b_fc2 = bias_variable([100])

h_fc2 = tf.nn.relu(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob)

#FCL 3
W_fc3 = weight_variable([100, 50])
b_fc3 = bias_variable([50])

h_fc3 = tf.nn.relu(tf.matmul(h_fc2_drop, W_fc3) + b_fc3)

h_fc3_drop = tf.nn.dropout(h_fc3, keep_prob)

#FCL 4
W_fc4 = weight_variable([50, 10])
b_fc4 = bias_variable([10])

h_fc4 = tf.nn.relu(tf.matmul(h_fc3_drop, W_fc4) + b_fc4)

h_fc4_drop = tf.nn.dropout(h_fc4, keep_prob)

#FCL 5
W_fc5 = weight_variable([10, OUT_SHAPE])
b_fc5 = bias_variable([OUT_SHAPE])

# This is the Output Layer, Classification Layer, etc...
y = tf.matmul(h_fc4_drop, W_fc5) + b_fc5
tf.add_to_collection('y', y)

# Learning Functions
global_step = tf.Variable(0, trainable=False)
tf.add_to_collection('global_step', global_step)

learn_rate = tf.train.exponential_decay(0.5,
                                        global_step,
                                        .05, 0.87,
                                        staircase=True,
                                        name="Learn_decay")
tf.add_to_collection('learn_rate', learn_rate)

train_vars = tf.trainable_variables()
loss = tf.reduce_mean(tf.square(tf.subtract(y_, y))) +\
			tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) *\
			0.001
tf.add_to_collection('loss', loss)

train_step = tf.train.AdamOptimizer(.001).minimize(loss, global_step)
tf.add_to_collection('train_op', train_step)

init_op = tf.global_variables_initializer()
tf.add_to_collection('init_op', init_op)

merged = tf.summary.merge_all()
tf.add_to_collection('merged', merged)

build_saver = tf.train.Saver()


"""

# Training loop variables
epochs = 1
batch_size = 100
num_samples = dataset_examples
step_size = int(num_samples / batch_size) # this was hardcoded in other examples

## DEPRICATED to its own FILE
class data_prep(object):
    def __init__(self, images, labels):
        self.index_in_epoch = 0
        self.num_examples = 0
        self.epochs_completed = 0
        self.num_examples = 0
        self.images = images
        self.labels = labels
        self.check_data()

    def check_data(self):
        try:
            assert self.images.shape[0] == self.labels.shape[0]
        except Exception as e:
            print("{} is not {}".format(self.images.shape[0], self.labels.shape[0]))
        self.num_examples = self.images.shape[0]
        return True

    def next_batch(self, batch_size, shuffle=False):
        #  Shuffle is off by default
        start = self.index_in_epoch
        self.index_in_epoch += batch_size
        if self.index_in_epoch > self.num_examples:
            # Finished epoch
            self.epochs_completed += 1
            # Shuffle the data
            if shuffle:
                perm = np.arange(self.num_examples)  # should add some sort of seeding for verification
                np.random.shuffle(perm)
                self.images = self.images[perm]
                self.labels = self.labels[perm]
            # Start next epoch
            start = 0
            self.index_in_epoch = batch_size
            assert batch_size <= self.num_examples
        end = self.index_in_epoch
        return self.images[start:end], self.labels[start:end]

data = data_prep(imgs, labels)
sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())
saver = tf.train.Saver()
iters = 10000
print("Training For {}".format(iters))
for i in tqdm(range(iters)):

    batch = data.next_batch(64)
    train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.65})
    if i%250 == 0:
        loss_value = sess.run(loss, feed_dict={x:batch[0], y_: batch[1], keep_prob: 1.0})

    if i%500 == 0:
        saver.save(sess, save_path + '/alphagriffin', global_step)
        tf.train.write_graph(sess.graph_def, save_path, 'alphagriffin.pbtxt')

## DONE
"""
