#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 17:23:42 2017

@author: eric
"""
import numpy as np


class mupenDataset(object):
    def __init__(self, imgs, labels, options=None):
        self.name                  = 'MUPEN64+'                         # ?? what does mupen mean?
        self.options               = options                            # MASTER: options should have everything
        self.imgs                  = imgs  # full path passed in
        self.labels                = labels  # full path passed in
        self.img_size              = None # is not square
        self.height                = 66
        self.width                 = 200
        self.num_channels          = 3
        self.num_classes           = 5 # technically this is the # of button inputs but i cant tell how its used here??
        self._epochs_completed     = 0
        self._index_in_epoch       = 0
        self._num_examples         = 0
        self.batch_size            = self.options.batch_size
        self.img_size_flat         = 13200
        
        # hacks
        self.trainer = self
        
        # startup
        self.build_return()
        
    def build_return(self):
        self._all_images_, self._all_labels_ = self.load(self.imgs,self.labels)
        self._num_examples         = self._all_images_.shape[0]
        if self.options.verbose: print ('ALL: images.shape: %s labels.shape: %s' % (self._all_images_.shape, self._all_labels_.shape))
        #this is a bad holder... because its a setup call...        
        _train_images, _train_labels, _test_images, _test_labels = self.split(self._all_images_, self._all_labels_)
        self.train_images = _train_images
        self.train_labels = _train_labels
        self.test_images = _test_images
        self.test_labels = _test_labels
        self.train_cls = np.array([label.argmax() for label in self.train_labels])
        self.test_cls = np.array([label.argmax() for label in self.test_labels])
        if self.options.verbose: print ('TRAIN: images.shape: %s labels.shape: %s' % (self.train_images.shape, self.train_labels.shape))
        if self.options.verbose: print ('TEST: images.shape: %s labels.shape: %s' % (self.test_images.shape, self.test_labels.shape)) 
        
    def load(self, images, labels):
        images = np.load(images)
        if self.options.verbose: print ("loaded {} images".format(len(images)))
        labels = np.load(labels)
        if self.options.verbose: print ("loaded {} labels".format(len(labels)))
        return images, labels
    
    def split(self, images, labels):
        size = len(images)
        if len(labels) < size: size = len(labels)
        train_size = int(0.8 * size)
        idx = np.random.permutation(size)

        idx_train = idx[0:train_size]
        idx_valid = idx[train_size:]

        train_images = images[idx_train, :]
        train_labels = labels[idx_train, :]

        test_images = images[idx_valid, :]
        test_labels = labels[idx_valid, :]

        return train_images, train_labels, test_images, test_labels
    
    def next_batch(self, batch_size,shuffle=False):
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            if shuffle:
                perm = np.arange(self._num_examples) # should add some sort of seeding for verification
                np.random.shuffle(perm)
                self._images = self._images[perm]
                self._labels = self._labels[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._all_images_[start:end], self._all_labels_[start:end], self._epochs_completed