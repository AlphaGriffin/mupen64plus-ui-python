# -*- coding: utf-8 -*-
# Author: Ruckusist and lannocc @ AlphaGriffin <Alphagriffin.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import tensorflow as tf
import time
from m64py.utils import need_dir
from m64py.tf.data_prep import DataPrep
from m64py.tf.build_network import MupenNetwork
import ag.logging as log


class Trainer():

    def __init__(self):
        log.debug()
        self.data_prep = DataPrep()
        self.model_network = MupenNetwork()

    def print(self, msg):
        print(msg)

    def select_data(self, load_dir, files):
        """Select the data.

        This has 3 steps
        -----------------
        * load numpy files and create a dataset
        * load and prep model params
        * create a new folder called work_dir/models/{game}/{game}model_{num}
        * save the model
        * combine dataset and model params and train dataset
        * save again and confim
        """
        log.debug()

        dataset = os.path.join(load_dir, files)
        self.print("Selected {} as Training Data Path".format(dataset))
        self.print("Loading Dataset...")
        self.active_dataset = self.data_prep.load_npz(dataset)

    def build_new_network(self, saveDir, currentGame):
        need_dir(saveDir)

        saveDir = os.path.join(saveDir, currentGame)
        need_dir(saveDir)

        model_fileName = "{}Model".format(currentGame)
        full_path = os.path.join(saveDir, model_fileName)
        need_dir(full_path)

        self.model_network.save_network(full_path)
        self.print("this is working!")

    def train_network(self, saveDir, currentGame, iters=5):
        saveDir = os.path.join(saveDir, currentGame)
        model_fileName = "{}Model".format(currentGame)
        model_path = os.path.join(saveDir, model_fileName)
        self.print("Loading Model From: {}".format(model_path))
        sess = tf.InteractiveSession()
        checkpoint_file = tf.train.latest_checkpoint(model_path)
        log.debug(checkpoint_file)
        new_saver = tf.train.import_meta_graph(checkpoint_file + ".meta")
        log.debug("found metagraph")
        sess.run(tf.global_variables_initializer())
        log.debug("init those variables")
        new_saver.restore(sess, checkpoint_file)
        self.print("this is working!")
        x = tf.get_collection('x_image')[0]
        # y = tf.get_collection('y')[0]
        y_ = tf.get_collection('y_')[0]
        keep_prob = tf.get_collection('keep_prob')[0]
        # loss = tf.get_collection('loss')[0]
        train = tf.get_collection('train_op')[0]
        # learn = tf.get_collection('learn_rate')[0]
        global_step = tf.get_collection_ref('global_step')[0]
        # writer = tf.summary.FileWriter(self.model_path)
        self.print("All variables loaded")

        iters = 100
        for i in range(iters):
            batch = self.data_prep.next_batch(64)
            self.print("Got batch for iter {}".format(i+1))
            feed_dict = {x: batch[0],
                         y_: batch[1],
                         keep_prob: 0.8}
            sess.run(train, feed_dict=feed_dict)
            g = sess.run(global_step)
            self.print("THIS IS WORKING!!! {}".format(g))
            if i % int(iters/10) == 0:
                self.print("this is SAVING!!!")
                new_saver.save(sess, model_path + '/Mupen64plus', global_step)
        sess.close()

