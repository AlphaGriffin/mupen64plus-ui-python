#!/usr/bin/env python

""" Mupen64 TF-DataPrep
Process the FilePath of Npz to Model, Model to Model, Model to Print

Alphagriffin.com
Eric Petersen @Ruckusist <eric.alphagriffin@gmail.com>
"""

import os
import time
import numpy as np

__author__ = "Eric Petersen @Ruckusist"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.1"
__maintainer__ = "Eric Petersen"
__email__ = "ruckusist@alphagriffin.com"
__status__ = "Prototype"


class DataPrep(object):
    def __init__(self):
        self.images = None
        self.labels = None

    def load_npz(self, path):
        load = np.load(path)
        images = load['images']
        labels = load['labels']
        self.images = images
        self.labels = labels
        return images, labels

"""
class Tester(object):
    def __init__(self):
        self.index_in_epoch = 0
        self.num_examples = 0
        self.epochs_completed = 0
        self.num_examples = 0
        self.images = None
        self.labels = None

    def load_npz(self, path):
        load = np.load(path)
        images = load['images']
        labels = load['labels']
        # self.images = images
        # self.labels = labels
        return images, labels


class TestPrep(object):
    def __init__(self):
        self.index_in_epoch = 0
        self.num_examples = 0
        self.epochs_completed = 0
        self.num_examples = 0
        self.images = None
        self.labels = None

    def load_npz(self, path):
        load = np.load(path)
        images = load['images']
        labels = load['labels']
        # self.images = images
        # self.labels = labels
        return images, labels

    def next_batch(self, batch_size, shuffle=False):
        #  Shuffle is off by default
        start = self.index_in_epoch
        self.index_in_epoch += batch_size
        if self.index_in_epoch > self.num_examples:
            # Finished epoch
            self.epochs_completed += 1
            # Shuffle the data
            if shuffle:
                perm = np.arange(self.num_examples)
                np.random.shuffle(perm)
                self.images = self.images[perm]
                self.labels = self.labels[perm]
            # Start next epoch
            start = 0
            self.index_in_epoch = batch_size
        end = self.index_in_epoch
        return self.images[start:end], self.labels[start:end]


"""