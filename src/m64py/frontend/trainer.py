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

import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'
import m64py.tf.model as model
import tensorflow as tf
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QAbstractItemView

from m64py.frontend.agblank import AGBlank
from m64py.tf.data_prep import DataPrep
from scratch.tf.mupen import mupenDataset as Data

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


class TfTraining(QThread):
    def setup(self, model_path, dataset_path, iters):
        sess = tf.InteractiveSession()
        # open dataset path first.
        self.dataset = DataPrep.load_npz(dataset_path)
        self.session = DataPrep.load_model(sess, model_path)
        self.model_path = model_path
        self.iters = iters
        # good
        return True

    def run(self):
        x = tf.get_collection('x_image')[0]
        print(x.name)
        y = tf.get_collection('y')[0]
        print(y.name)
        y_ = tf.get_collection('y_')[0]
        print(y.name)
        keep_prob = tf.get_collection('keep_prob')[0]
        print(keep_prob.name)
        loss = tf.get_collection('loss')[0]
        print(loss.name)
        train = tf.get_collection('train_op')[0]
        print(train.name)
        learn = tf.get_collection('learn_rate')[0]
        print(learn.name)
        global_step = tf.get_collection_ref('global_step')[0]
        print(global_step.name)
        init_op = tf.get_collection_ref('init_op')[0]
        print(init_op.name)
        merged = tf.get_collection_ref('merged')[0]
        print(merged.name)

        # Need a Saver and a Writer
        saver = tf.train.Saver()
        writer = tf.summary.FileWriter(self.model_path)

        # Training loop variables
        batch_size = 50
        iters = 100
        for i in range(iters):
            batch = data.next_batch(batch_size)
            feed_dict = {x: batch[0],
                         y_: batch[1],
                         keep_prob: 0.8}
            sess.run(train)
            g = sess.run(global_step)

            if i % int(iters/10) == 0:
                saver.save(sess, self.model_path, global_step)
                writer.add_summary(summary, int(g+i))
        
    def tfStop(self):
        self.session.close()


class Trainer(AGBlank):
    """AG_Trainer Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        super().__init__(parent)
        self.parent = parent
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
        
        # get references
        self.trainer_thread = TfTraining(parent=self.parent)

        # booleans
        self.processing = False
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
        self.selected = None
        self.selection = []
        self.selectedRom = ""
        self.gamePath = ""
        self.load_dir = ""
        self.selectingRom = True
        
        # Use the processor
        self.worker = worker
        self.root_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.root_dir, "datasets")
        self.save_dir = os.path.join(self.root_dir, "model")


        # Startup Processes
        self.getSaves()

    """TEST FUNCTIONS"""
    def load_dataset(self, loadir, files):
        # check file integrity
        has_image_file = False
        has_labels_file = False
        for file in files:
            file = os.path.join(self.load_dir, file)
            if os.path.isfile(file):
                if "image" in file:
                    has_image_file = True
                    #print("Image File: {}".format(file))
                    self.image_file = file
                if "label" in file:
                    has_labels_file = True
                    #print("Label File: {}".format(file))
                    self.label_file = file
            else:
                print("Bad File name given: {}".format(file))
        if has_image_file and has_labels_file:
            # import the dataset can opener
            self.print_console("Loading Dataset:\n\tImages{}\n\tLabels: {}".format(self.image_file,
                                                                                   self.label_file))
            self.active_dataset = Data(self.image_file, self.label_file)
            self.print_console(self.active_dataset.msg)
            return True
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
        loaddir = os.path.join(self.root_dir, "datasets", self.currentGame)

        # data = self.load_dataset(loadir, files)
        if not data:
            return False
        self.print_console("Selected {} as Training Data Path".format(loaddir))
        self.active_dataset = loaddir
        self.actionButton.setEnabled(True)
        return True

    def build_new_network(self):
        saveDir = os.path.join(self.root_dir, "model", self.currentGame)
        model_fileName = "{}.tfmupen".format(self.currentGame)
        full_path = os.path.join(saveDir, model_fileName)
        if os.path.isdir(saveDir):
            self.print_console("A Model Already Exists for this game: {}".format(saveDir))
            # TODO: do you want to delete it and make a new one?
            return full_path
        else:
            self.print_console("Creating folder: {}".format(saveDir))
            os.mkdir(saveDir)
            with tf.Session as sess:
                from m64py.tf.build_network import *






    def train_network(self, iters=5):
        saveDir = os.path.join(self.root_dir, "model", self.currentGame)
        model_fileName = "{}_playbackModel.ckpt".format(self.currentGame)

        if not os.path.isdir(saveDir):
            self.print_console("Creating folder: {}".format(saveDir))
            os.mkdir(saveDir)

        datasetIndex = len(os.listdir(saveDir))
        model_savePath = os.path.join(saveDir, "playbackModel_{}".format(datasetIndex))

        if not os.path.isdir(model_savePath):
            self.print_console("Creating folder: {}".format(model_savePath))
            os.mkdir(model_savePath)

        model_fileName = os.path.join(model_savePath, model_fileName)
        # start threading processes
        print(self.active_dataset.msg)
        self.trainer_thread.setup(model_fileName, self.active_dataset, iters)
        self.print_console("#############################################")
        self.print_console("# Processing dataset to Playback Model")
        self.print_console("# Game Name: {}".format(self.currentGame))
        self.print_console("# Dataset Path: {}".format(model_savePath))
        self.print_console("# Number of Iterations to Train: {}".format(iters))
        try:
            self.trainer_thread.start()
            self.print_console("Greetings Prof. Falcon," +
                               "\tWould you like to play a game?")

        except Exception as e:
            self.print_console("SHIT!... this is the error:\n{}\nSHIT!".format(e))

        finally:
            self.print_console("# Finished Training Model!")
            self.print_console("#############################################")


    """Selector FUNCTIONS"""
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
        self.input.setText("100")
        self.selection = selection
        
        # if we have picked a game
        if any(select_string in s for s in self.gamesList):
            if not self.currentGame:
                self.currentGame = self.selected[0].text()
                self.load_dir = os.path.join(self.work_dir, self.currentGame)
                self.print_console("Game Save Dir: {}".format(self.load_dir))
            self.selectingRom = False

            if os.path.isdir(self.load_dir):
                self.build_selector(folder=self.load_dir)
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
        iters = self.input.text()
        self.train_network(iters=iters)
        pass
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        self.select_data()
        pass
         
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        self.selected = self.selector.selectedItems()
        if len(self.selected) > 0:
            self.selecterator()
            return
        self.actionButton.setEnabled(False)
        
    @pyqtSlot()
    def closeEvent(self, event=False): pass
