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

    def __init__(self, options, imgs=False, labels=False):
        self.name = 'MUPEN64+'
        self.options = options
        self.imgs = imgs  # full path passed in
        self.labels = labels  # full path passed in
        self.img_size = None  # is not square
        self.height = 66
        self.width = 200
        self.num_channels = 3
        self.num_classes = 5
        self.batch_size = self.options.batch_size
        self.img_size_flat = self.width * self.height

        # Necessary Placeholders for working being done
        self._epochs_completed = 0
        self._index_in_epoch = 0
        self._num_examples = 0

        # hacks
        self.trainer = self

        # startup
        if imgs:
            self.build_return()

    def build_return(self):
        """ This opens the files and does the label argmax for you"""
        # probably _ all stuffs _ is a bad name for stuff ... bud it shouldnt be used
        self._all_images_, self._all_labels_ = self.load(self.imgs, self.labels)

        # this is used for a bunch of stuff
        self._num_examples = self._all_images_.shape[0]

        # split up Alldata into some chunks we can use
        self.train_images, self.train_labels, self.test_images, self.test_labels = self.split(self._all_images_,
                                                                                              self._all_labels_)
        self.train_cls = np.array([label.argmax() for label in self.train_labels])
        self.test_cls = np.array([label.argmax() for label in self.test_labels])

        # This is good to know things are working
        if self.options.verbose: print(
            'ALL: images.shape: %s labels.shape: %s' % (self._all_images_.shape, self._all_labels_.shape))
        if self.options.verbose: print(
            'TRAIN: images.shape: %s labels.shape: %s' % (self.train_images.shape, self.train_labels.shape))
        if self.options.verbose: print(
            'TEST: images.shape: %s labels.shape: %s' % (self.test_images.shape, self.test_labels.shape))

    def load(self, images, labels):
        """ Load 2 numpy objects as a set images, labels in: paths, out: np.arrays"""
        images = np.load(images)
        if self.options.verbose: print("loaded {} images".format(len(images)))
        labels = np.load(labels)
        if self.options.verbose: print("loaded {} labels".format(len(labels)))
        return images, labels

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

    def next_batch2(self, batch_size, shuffle=False, test=False):
        """
        Shuffle is off by default
        Test is off by default... switches which set to take batch from
        """
        # which set are we using??
        images = self.train_images
        labels = self.train_labels
        if test:
            images = self.test_images
            labels = self.test_labels

        # get our start postition
        start = self._index_in_epoch
        self._index_in_epoch += batch_size

        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1

            # Shuffle the data
            if shuffle:
                perm = np.arange(self._num_examples)  # should add some sort of seeding for verification
                np.random.shuffle(perm)
                images = images[perm]
                labels = labels[perm]

            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch

        # batch check
        # if len(images) is not len(labels):
        #    return False
        return images[start:end], labels[start:end], self._epochs_completed

    def next_batch(self, batch_size, shuffle=False):
        """ Shuffle is off by default """
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            if shuffle:
                perm = np.arange(self._num_examples)  # should add some sort of seeding for verification
                np.random.shuffle(perm)
                self._images = self._images[perm]
                self._labels = self._labels[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._all_images_[start:end], self._all_labels_[start:end]