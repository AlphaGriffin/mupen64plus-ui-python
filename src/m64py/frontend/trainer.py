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
from m64py.tf.mupen import mupenDataset as Data
import m64py.tf.model as model
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QAbstractItemView
import os, sys
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


class TfTraining(QThread):
    def setup(self, model_savePath, active_dataset):
        print("TF Version: {}\nModules loaded Properly!".format(tf.__version__))
        print("FileName = {}\nFinal Layer: {}".format(model_savePath, model.y))
        
        self.model_savePath = model_savePath
        self.active_dataset = active_dataset
        # self.model_ = model_
        self.session = tf.InteractiveSession()
        print("finished setup")

    def run(self):
        print("start")
        sess = self.session
        # model = self.model_
        data = self.active_dataset
        print("RUN - 1\n{}\n{}".format(model.y, data.msg))
        # import m64py.tf.model as model
        print("RUN - 2 Session Model Final Layer: {}".format(model.y_))
        # Learning Functions
        L2NormConst = 0.001
        self.session.run(tf.global_variables_initializer())
        train_vars = tf.trainable_variables()
        print("RUN - 3 train_vars: {}".format(train_vars))
        cost = tf.square(tf.subtract(model.y_, model.y))
        print("RUN - 4")
        # trained_vars = tf.add_n([tf.nn.l2_loss(v) for v in train_vars])
        print("RUN - 5")
        loss = tf.reduce_mean(cost) * .01# + trained_vars * .01
        print("RUN - 6")
        train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)
        print("RUN - 7")
        # self.session.run(tf.global_variables_initializer())
        print("RUN - 8")
        # Training loop variables
        epochs = 2
        batch_size = 50
        num_samples = data.num_examples
        step_size = int(num_samples / batch_size)
        loss_value = 0
        print("RUN - 9 step_size: {}".format(step_size))
        for epoch in range(epochs):
            print("im looping out bro! epoch in epochs: {}/{}".format(epoch, epochs))
            for i in range(step_size):
                batch = data.next_batch(batch_size)

                train_step.run(sess=self.session, feed_dict={model.x: batch[0],
                                                             model.y_: batch[1],
                                                             model.keep_prob: 0.8})

                if i % 10 == 0:
                    loss_value = loss.eval(sess=self.session, feed_dict={model.x: batch[0],
                                                                         model.y_: batch[1],
                                                                         model.keep_prob: 1.0})
                    print("epoch: %d step: %d loss: %g"%(epoch, epoch * batch_size + i, loss_value))

        # Save the Model
        saver = tf.train.Saver(var_list={"{}".format(v): v for v in [tf.model_variables()]})
        saver.save(sess, "{}".format(self.model_savePath))
        print("SAVED! : {}".format(self.model_savePath))
        return loss_value
        
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
        loadir = os.path.join(self.root_dir, "datasets", self.currentGame)

        data = self.load_dataset(loadir, files)
        if not data:
            return False
        # self.print_console(data.msg)
        # self.active_dataset = data
        self.actionButton.setEnabled(True)
        return True

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
        self.trainer_thread.setup(model_fileName, self.active_dataset)
        self.print_console("#############################################")
        self.print_console("# Processing dataset to Playback Model")
        self.print_console("# Game Name: {}".format(self.currentGame))
        self.print_console("# Dataset Path: {}".format(model_savePath))
        self.print_console("# Number of Iterations to Train: {}".format(iters))
        self.print_console("#############################################")
        try:
            self.trainer_thread.start()
            # self.print_console("Completed Training! the AI now EXISTS\nTraining Loss: {}".format(self.train_loss))
            self.print_console("Greetings Prof. Falcon," +
                               "\tWould you like to play a game?")

        except Exception as e:
            self.print_console("SHIT!... this is the error:\n{}\nSHIT!".format(e))

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
