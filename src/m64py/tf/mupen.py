#!/usr/bin/python3
"""
Ruckusist @ alphagriffin.com
"""
import numpy as np
### IM HAVING A SEED PROBLEM!!!

class mupenDataset(object):
    """ 
    This is a Tensorflow Input Data Class... most of this output are required
    field for using the Advanced ModelBuilder and Processor
    
    TODO:
    -----
    (1) redo this whole thing with more sensible human readable labels
    (2) make a kickass human readable printout for .rst and console
        
    """
    def __init__(self, imgs=None, labels=None, init=True):
        self.name                  = 'MUPEN64+'
        self.imgs                  = imgs    # full path passed in
        self.labels                = labels  # full path passed in
        self.img_size              = None    # is not square
        self.height                = 66
        self.width                 = 200
        self.num_channels          = 3
        self.num_classes           = 5  # technically this is the # of button inputs but i cant tell how its used here??
        self.img_size_flat         = self.width * self.height
        
        # Necessary Placeholders for working being done
        self._epochs_completed     = 0
        self._index_in_epoch       = 0
        self._num_examples         = 1
        
        # hacks
        self.trainer = self
        
        # startup
        self.msg = "Loading Numpy Dataset"
        self.msg += "Images: {} ".format(str(imgs))
        self.msg += "Labels: {} ".format(str(labels))
        # print(self.msg)
        if init:
            self.build_return()
        
    def build_return(self):
        """ This opens the files and does the label argmax for you"""
        # probably _ all stuffs _ is a bad name for stuff ... bud it shouldnt be used
        #print("DEBUGS = data 0")
        self._all_images_, self._all_labels_ = self.load(self.imgs, self.labels)
        #print("DEBUGS-data 1")
        # this is used for a bunch of stuff
        self._num_examples = self._all_images_.shape[0]
        
        # split up Alldata into some chunks we can use 
        #self.train_images, self.train_labels, self.test_images, self.test_labels = self.split(self._all_images_, self._all_labels_)
        self.train_cls = np.array([label.argmax() for label in self._all_labels_])
        self.test_cls = np.array([label.argmax() for label in self._all_labels_])
        
        # This is good to know things are working
        self.msg = "ALL: images.shape: {} labels.shape: {}".format(self._all_images_.shape, self._all_labels_.shape)
        #self.msg += "TRAIN: images.shape: {} labels.shape: {}".format(self.train_images.shape, self.train_labels.shape)
        #self.msg += "'TEST: images.shape: {} labels.shape: {}".format(self.test_images.shape, self.test_labels.shape)
        # print(self.msg)
        # print("DEBUGS - data 2")
        
    def load(self, images, labels):
        """ Load 2 numpy objects as a set images, labels in: paths, out: np.arrays"""
        images = np.load(images)
        print("loaded {} images".format(len(images)))
        labels = np.load(labels)
        print("loaded {} labels".format(len(labels)))
        return images, labels

    @staticmethod
    def split(self, images, labels):
        """ Split the dataset in to different groups for many reasons"""
        # this needs a SEED !!! OMG !!!!
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

    def next_batch(self, batch_size):
        """ Shuffle is off by default """
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._all_images_[start:end], self._all_labels_[start:end], self._epochs_completed
