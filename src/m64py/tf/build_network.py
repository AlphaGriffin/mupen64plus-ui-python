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


class MupenNetwork(object):
    def __init__(self):
        self.IMG_W = 200
        self.IMG_H = 66
        self.OUT_SHAPE = 5
        pass

    def weight_variable(self, shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    def bias_variable(self, shape):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)

    def conv2d(self, x, W, stride):
        return tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding='VALID')

    def save_network(self, path):
        with tf.Session() as sess:
            self.build_network()
            saver = tf.train.Saver()
            sess.run(tf.global_variables_initializer())
            saver.save(sess, path + "/Mupen64plus")
            print("New Model Save")
        return True

    def build_network(self):
        self.x = tf.placeholder(tf.float32, shape=[None, self.IMG_H, self.IMG_W, 3])
        self.y_ = tf.placeholder(tf.float32, shape=[None, self.OUT_SHAPE])
        self.x_image = self.x
        tf.add_to_collection('x_image',self.x_image)
        tf.add_to_collection('y_', self.y_)

        self.W_conv1 = self.weight_variable([5, 5, 3, 16])
        self.b_conv1 = self.bias_variable([16])
        self.h_conv1 = tf.nn.relu(self.conv2d(self.x_image, self.W_conv1, 2) + self.b_conv1)

        #second convolutional layer
        self.W_conv2 = self.weight_variable([5, 5, 16, 36])
        self.b_conv2 = self.bias_variable([36])
        self.h_conv2 = tf.nn.relu(self.conv2d(self.h_conv1, self.W_conv2, 2) + self.b_conv2)

        #third convolutional layer
        self.W_conv3 = self.weight_variable([5, 5, 36, 48])
        self.b_conv3 = self.bias_variable([48])
        self.h_conv3 = tf.nn.relu(self.conv2d(self.h_conv2, self.W_conv3, 2) + self.b_conv3)

        #fourth convolutional layer
        self.W_conv4 = self.weight_variable([3, 3, 48, 64])
        self.b_conv4 = self.bias_variable([64])
        self.h_conv4 = tf.nn.relu(self.conv2d(self.h_conv3, self.W_conv4, 1) + self.b_conv4)

        #fifth convolutional layer
        self.W_conv5 = self.weight_variable([3, 3, 64, 64])
        self.b_conv5 = self.bias_variable([64])
        self.h_conv5 = tf.nn.relu(self.conv2d(self.h_conv4, self.W_conv5, 1) + self.b_conv5)

        # Flatten Layer
        self.h_conv5_flat = tf.reshape(self.h_conv5, [-1, 1152])

        #FCL 1
        self.W_fc1 = self.weight_variable([1152, 1164])
        self.b_fc1 = self.bias_variable([1164])
        self.h_fc1 = tf.nn.relu(tf.matmul(self.h_conv5_flat, self.W_fc1) + self.b_fc1)

        # Start Adding a Dropout for awesomeness .8 is given but mess with it
        self.keep_prob = tf.placeholder(tf.float32)
        tf.add_to_collection('keep_prob', self.keep_prob)
        self.h_fc1_drop = tf.nn.dropout(self.h_fc1, self.keep_prob)

        #FCL 2
        self.W_fc2 = self.weight_variable([1164, 100])
        self.b_fc2 = self.bias_variable([100])

        self.h_fc2 = tf.nn.relu(tf.matmul(self.h_fc1_drop, self.W_fc2) + self.b_fc2)

        self.h_fc2_drop = tf.nn.dropout(self.h_fc2, self.keep_prob)

        #FCL 3
        self.W_fc3 = self.weight_variable([100, 50])
        self.b_fc3 = self.bias_variable([50])

        self.h_fc3 = tf.nn.relu(tf.matmul(self.h_fc2_drop, self.W_fc3) + self.b_fc3)

        self.h_fc3_drop = tf.nn.dropout(self.h_fc3, self.keep_prob)

        #FCL 4
        self.W_fc4 = self.weight_variable([50, 10])
        self.b_fc4 = self.bias_variable([10])

        self.h_fc4 = tf.nn.relu(tf.matmul(self.h_fc3_drop, self.W_fc4) + self.b_fc4)

        self.h_fc4_drop = tf.nn.dropout(self.h_fc4, self.keep_prob)

        #FCL 5
        self.W_fc5 = self.weight_variable([10, self.OUT_SHAPE])
        self.b_fc5 = self.bias_variable([self.OUT_SHAPE])

        # This is the Output Layer, Classification Layer, etc...
        self.y = tf.matmul(self.h_fc4_drop, self.W_fc5) + self.b_fc5
        tf.add_to_collection('y', self.y)

        # Learning Functions
        self.global_step = tf.Variable(0, trainable=False)
        tf.add_to_collection('global_step', self.global_step)

        self.learn_rate = tf.train.exponential_decay(0.5,
                                                self.global_step,
                                                .05, 0.87,
                                                staircase=True,
                                                name="Learn_decay")
        tf.add_to_collection('learn_rate', self.learn_rate)

        self.train_vars = tf.trainable_variables()
        self.loss = tf.reduce_mean(tf.square(tf.subtract(self.y_, self.y))) +\
        			tf.add_n([tf.nn.l2_loss(v) for v in self.train_vars]) *\
        			0.001
        tf.add_to_collection('loss', self.loss)

        self.train_step = tf.train.AdamOptimizer(.001).minimize(self.loss, self.global_step)
        tf.add_to_collection('train_op', self.train_step)
