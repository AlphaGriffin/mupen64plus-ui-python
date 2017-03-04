# -*- coding: utf-8 -*-
# Author: Ruckusist @ AlphaGriffin <Alphagriffin.com>
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

from m64py.frontend.agblank import AGBlank
from m64py.tf.mupen import mupenDataset as data
import m64py.tf.model as model
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QAbstractItemView
from glob import glob
import os, sys
import numpy as np
import tensorflow as tf
pyVERSION = sys.version
tfVERSION = tf.__version__
INTRO =\
"""
Tensorflow Model Creation and Training SOFTWARE:
    Python Version: {}
    Tensorflow Version: {}
    Step 1 - Choose a Dataset.
    
    Step 2 - Click Train New Model. Visit AlphaGriffin.com for other ways and
    tools to train models. Make sure to Train at least 1 iteration and save
    the model. 
    
    Step 3  - Then either (1) Load and Optimize your existing model or 
    (2) take the model to Alphagriffin.com or your own AWS for further
    optimization.


""".format(pyVERSION, tfVERSION)

class ServerThread(QThread):
    """Thread for running the web server"""

    def set_server(self, server):
        self.server = server

    def run(self):
        self.server.serve_forver()

class tf_training(QThread):
    def setup(self, model_savePath, active_dataset, model_):        
        print("TF Version: {}\nModules loaded Properly!".format(tf.__version__))
        print("Filename = {}\nFinal Layer: {}".format(model_savePath, model_.y))
        
        self.model_savePath = model_savePath
        self.active_dataset = active_dataset
        self.model_ = _MODEL_

    def run(self, sess=None):
        model = self.model_
        data = self.active_dataset
        # Start session
        if sess is None:
            sess = tf.InteractiveSession()
        self.session = sess
        # Learning Functions
        L2NormConst = 0.001
        train_vars = tf.trainable_variables()
        loss = tf.reduce_mean(tf.square(tf.subtract(model.y_, model.y))) + tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) * L2NormConst
        train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

        sess.run(tf.global_variables_initializer())

        # Training loop variables
        epochs = 2
        batch_size = 50
        num_samples = data.num_examples
        step_size = int(num_samples / batch_size)
        loss_value = 0
        for epoch in range(epochs):
            for i in range(step_size):
                batch = data.next_batch(batch_size)

                train_step.run(feed_dict={model.x: batch[0], model.y_: batch[1], model.keep_prob: 0.8})

                if i%10 == 0:
                  loss_value = loss.eval(feed_dict={model.x:batch[0], model.y_: batch[1], model.keep_prob: 1.0})
                  print("epoch: %d step: %d loss: %g"%(epoch, epoch * batch_size + i, loss_value))

        # Save the Model
        saver = tf.train.Saver(var_list={"{}".format(v): v for v in [tf.model_variables()]})
        saver.save(sess, "{}.ckpt".format(self.model_savePath))
        return loss_value
        
    def tfStop(self):
        self.session.close()

class Trainer(AGBlank):
    """AG_Trainer Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        super().__init__(parent)
        self.setWindowTitle('AG Trainer')
        self.selectorLabel.setText('Existing Save Folders:')
        self.selector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.inputLabel.setText('Working Directory(s):')
        self.actionButton.setText('Process')
        self.actionButton.setEnabled(False)
        self.actionButton.setText('Train New Model')
        self.checkButton.setEnabled(False)
        self.checkButton.setText('Load/Optimize')
        self.input.setEnabled(False)
        self.selector.setEnabled(False)
        
        # booleans
        self.processing = False
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
        self.selected = None
        self.selection = []
        self.selectedRom = ""
        self.gamePath = ""
        self.selectingRom = True
        
        # Use the processor
        self.worker = worker
        self.root_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.root_dir, "dataset")
        self.save_dir = os.path.join(self.root_dir, "model")
        
        self.getSaves()
        
        
    """ TEST FUNCTIONS """
    def load_dataset(self, loadDir, files):
        # check file integrity
        has_image_file = False
        has_labels_file = False
        for file in files:
            print(file)
            file = glob(os.path.join(loadDir, file))
            if os.path.isfile(file):
                if "image" in file:
                    has_image_file = True
                    print("Image File: {}".format(file))
                    self.image_file = file
                if "label" in file:
                    has_label_file = True
                    print("Label File: {}".format(file))
                    self.label_file  = file
            else:
                print("Bad File name given: {}".format(file))
        if has_image_file and has_label_file:
            # import the dataset can opener
            dataset, msg = data(self.image_file, self.label_file)
            return dataset, msg
        else:
            "File Names  were no good..."
            return False

    def select_data(self):
        """
        This has 3 steps
        -----------------
        * load numpy files and create a dataset
        * load and prep model params
        * create a new folder called work_dir/models/{game}/{game}model_{num}
        * save the model 
        * combine dataset and model params and train dataset
        * save again and confim
        """
        files = self.selection
        loadDir = os.path.join(self.root_dir, "datasets", self.currentGame)     
        
        data_splitset, msg = self.load_dataset(loadDir, files)
        if not data_splitset:
            return False
        self.print_console(msg)
        self.active_dataset = data_splitset
        self.actionButton.setEnabled(True)
        return True

    def train_network(self, iters=5):
        model_ = model()
        self.print_console(model.msg)
        saveDir = os.path.join(self.root_dir, "model", self.currentGame)   
        if not os.path.isdir(saveDir):
            self.print_console("Creating folder: {}".format(saveDir))
            os.mkdir(saveDir)
        datasetIndex = len(os.listdir(saveDir))
        model_savePath = os.path.join(saveDir, "playbackModel_{}".format(datasetIndex))
        if not os.path.isdir(model_savePath):
            self.print_console("Creating folder: {}".format(saveDir))
            os.mkdir(model_savePath)
        model_fileName = "{}_playbackModel".format(self.currentGame)
        self.print_console("#############################################")
        self.print_console("# Processing dataset to Playback Model")
        self.print_console("# Game Name: {}".format(self.currentGame))
        self.print_console("# Dataset Path: {}".format(model_savePath))
        self.print_console("# Number of Iterations to Train: {}".format(iters))
        self.print_console("#############################################")
        filename = os.path.join(self.model_savePath, self.model_fileName)
        self.train_loss = tf_training(filename, self.active_dataset, model_)
        self.print_console("Completed Training! the AI now EXISTS\nTraining Loss: {}".format(train_loss))
        self.print_console("Greetings Prof. Falcon," +
                           "\tWould you like to play a game?")
      
    
    """ Selector FUNCTIONS """
    def getSaves(self):
        """
        Creates a list of Datasets for the selected game.
        """
        try:
            self.gamesList = os.listdir(self.work_dir)
        except FileNotFoundError:
            self.print_console("Source path does not exist: {}".format(
                               self.work_dir))
            return

        self.selector.setEnabled(True)
        self.selectingRom = True
        self.actionButton.setEnabled(False)
        self.checkButton.setEnabled(False)
        self.currentGame = False
        self.build_selector()
        
    def selecterator(self):
        """
        Make sure the finiky QWidget List selector doesnt crash the system.
        """
        selection = []
        
        # get self.selected from a global but this is a less good solution
        for x in self.selected:
            selection.append(x.text())
        select_string = ", ".join(x for x in selection)
        self.input.setText(select_string)
        self.selection = selection
        
        # if we have picked a game
        if any(select_string in s for s in self.gamesList):
            self.currentGame = self.selected[0].text()
            self.selectingRom = False
            x = os.path.join(self.work_dir,self.currentGame)
            if os.path.isdir(x):
                self.print_console("Game Save Dir: {}".format(x))
                self.build_selector(folder=x)
                return
        
        # if we need to go back and pick a different game
        if len(select_string) is 3:
            self.print_console("going back to choose another game!")
            self.getSaves()
            return
            
        # if we have a list of Dirs to work on ...
        self.checkButton.setEnabled(True)
        # click on the button!!!
                   
    def build_selector(self, folder=""):
        """This populates the save folder list"""
        self.selector.clear()
        if not self.selectingRom or folder is not "": 
            self.selector.addItem("../")
            for i in sorted(os.listdir(folder)):
                self.selector.addItem("{}".format(i))   
        else:
            for i in self.gamesList:
                self.selector.addItem("{}".format(i))
        """then we need to be selecting folders to process"""
    
    def show(self):
        """On Show this window"""
        super().show()
        
    def hide(self):
        """On hide this window"""
        super().hide()
    
    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Start Training the model"""
        self.train_network()
        pass
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        self.select_data()
        """Test Button for pressing broken parts"""
        pass
         
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        self.selected = self.selector.selectedItems()
        if len(self.selected) > 0:
            self.selecterator()
            return
        self.actionButton.setEnabled(False)
        
    @pyqtSlot()
    def closeEvent(self,event=False): pass
