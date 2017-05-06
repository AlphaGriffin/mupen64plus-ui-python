#!/usr/bin/env python

""" Mupen64 TF-DataPrep
Process the FilePath of Npz to Model, Model to Model, Model to Print

Alphagriffin.com
Eric Petersen @Ruckusist <eric.alphagriffin@gmail.com>
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'
import numpy as np
import tensorflow as tf

__author__ = "Eric Petersen @Ruckusist"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.1"
__maintainer__ = "Eric Petersen"
__email__ = "ruckusist@alphagriffin.com"
__status__ = "Prototype"


class DataPrep(object):
    def __init__(self):
        self.index_in_epoch = 0
        self.num_examples = 0
        self.epochs_completed = 0
        self.num_examples = 0
        self.images = None
        self.labels = None

    def load_model(self, sess, path):
        checkpoint_file = tf.train.latest_checkpoint(path)
        meta_path = checkpoint_file + ".meta"
        saver = tf.train.import_meta_graph(meta_path)
        sess.run(tf.global_variables_initializer())
        saver.restore(sess, checkpoint_file)
        return sess

    def load_npz(self, path):
        load = np.load(path)
        self.images = load['images']
        self.labels = load['labels']
        if self.check_data():
            return self.images, self.labels

    def check_data(self):
        assert self.images.shape[0] == self.labels.shape[0]
        self.num_examples = self.images.shape[0]

    def next_batch(self, batch_size, shuffle=False):
        """ Shuffle is off by default """
        start = self.index_in_epoch
        self.index_in_epoch += batch_size
        if self.index_in_epoch > self.num_examples:
            # Finished epoch
            self.epochs_completed += 1
            # Shuffle the data
            if shuffle:
                # should add some sort of seeding for verification
                perm = np.arange(self.num_examples)
                np.random.shuffle(perm)
                self.images = self.images[perm]
                self.labels = self.labels[perm]
            # Start next epoch
            start = 0
            self.index_in_epoch = batch_size
            assert batch_size <= self.num_examples
        end = self.index_in_epoch
        return self.images[start:end], self.labels[start:end]