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
import sys
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QAbstractItemView
from m64py.frontend.agblank import AGBlank
import ag.logging as log


class Training(QThread):

    def __init__(self, ui):
        log.debug()
        QThread.__init__(self, ui)
        self.ui = ui
        self.state = 0

    def run(self):
        log.debug()
        try:
            self.ui.status("Importing Python modules...")
            import tensorflow as tf
            import time
            from m64py.tf.data_prep import DataPrep
            from m64py.tf.build_network import MupenNetwork
            self.ui.status("Ready for training.")

            self.tf = tf
            self.data_prep = DataPrep()
            self.model_network = MupenNetwork()

            while self.state >= 0:
                time.sleep(0)  # yield to other threads

                if self.state == 1:
                    self.select_data()
                    self.state = 0

                elif self.state == 2:
                    self.build_new_network()
                    self.state = 0

                elif self.state == 3:
                    self.train_network()
                    self.state = 0

        except Exception as e:
            log.fatal()
            self.ui.status("Error in Trainer Worker thread: {}".format(e))

    def select_data(self):
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
        self.ui.status("Loading Dataset...")

        files = self.ui.selection[0]
        dataset = os.path.join(
            self.ui.root_dir, "datasets", self.ui.currentGame, files)
        self.ui.print_console(
                "Selected {} as Training Data Path".format(dataset))
        self.ui.print_console("Loading Dataset...")
        self.active_dataset = self.data_prep.load_npz(dataset)
        self.ui.actionButton.setEnabled(True)

        self.ui.status("Dataset loaded.")
        return True

    def build_new_network(self):
        self.ui.status("Building Network...")

        saveDir = os.path.join(self.ui.root_dir, "model", self.ui.currentGame)
        self.ui.print_console("{}".format(saveDir))
        model_fileName = "{}Model".format(self.ui.currentGame)
        full_path = os.path.join(saveDir, model_fileName)
        self.ui.print_console("{}".format(full_path))
        try:
            os.mkdir(full_path)
        except Exception as e:
            self.ui.print_console("{}".format(e))
            try:
                os.mkdir(saveDir)
                os.mkdir(full_path)
                pass
            except Exception as e:
                self.ui.print_console("{}".format(e))
        self.ui.print_console("created a new directory {}".format(full_path))
        self.model_network.save_network(full_path)
        self.ui.print_console("this is working!")

        self.ui.status("Network built.")

    def train_network(self, iters=5):
        self.ui.status("Training Network...")

        tf = self.tf
        saveDir = os.path.join(self.ui.root_dir, "model", self.ui.currentGame)
        model_fileName = "{}Model".format(self.ui.currentGame)
        model_path = os.path.join(saveDir, model_fileName)
        self.ui.print_console("Loading Model From: {}".format(model_path))
        sess = tf.InteractiveSession()
        checkpoint_file = tf.train.latest_checkpoint(model_path)
        print(checkpoint_file)
        new_saver = tf.train.import_meta_graph(checkpoint_file + ".meta")
        print("found metagraph")
        sess.run(tf.global_variables_initializer())
        print("init those variables")
        new_saver.restore(sess, checkpoint_file)
        self.ui.print_console("this is working!")
        x = tf.get_collection('x_image')[0]
        # y = tf.get_collection('y')[0]
        y_ = tf.get_collection('y_')[0]
        keep_prob = tf.get_collection('keep_prob')[0]
        # loss = tf.get_collection('loss')[0]
        train = tf.get_collection('train_op')[0]
        # learn = tf.get_collection('learn_rate')[0]
        global_step = tf.get_collection_ref('global_step')[0]
        # writer = tf.summary.FileWriter(self.model_path)
        self.ui.print_console("All variables loaded")

        iters = 100
        for i in range(iters):
            batch = self.data_prep.next_batch(64)
            self.ui.print_console("Got batch for iter {}".format(i+1))
            feed_dict = {x: batch[0],
                         y_: batch[1],
                         keep_prob: 0.8}
            sess.run(train, feed_dict=feed_dict)
            g = sess.run(global_step)
            self.ui.print_console("THIS IS WORKING!!! {}".format(g))
            if i % int(iters/10):
                new_saver.save(sess, model_path + '/Mupen64plus', global_step)
            self.ui.print_console("this is SAVING!!!")
        sess.close()

        self.ui.status("Network trained.")


class Trainer(AGBlank):
    """AG_Trainer Widget of MuPen64 Python Ui."""

    def __init__(self, parent, status, worker):
        """Init Stuff."""
        super().__init__(parent, status)
        self.parent = parent
        self.setWindowTitle('AG Trainer')
        self.selectorLabel.setText('Existing Save Folders:')
        self.selector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.inputLabel.setText('Working Directory(s):')
        self.actionButton.setEnabled(False)
        self.actionButton.setText('Optimize')
        self.checkButton.setEnabled(False)
        self.checkButton.setText('Data Load')
        self.check2Button.setEnabled(False)
        self.check2Button.setText('Model Load')
        self.input.setEnabled(False)
        self.selector.setEnabled(False)

        # get references
        self.process = Worker(self)
        self.process.start()
        '''
        self.data_prep = DataPrep()
        self.model_network = MupenNetwork()
        '''

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
        self.currentGame = None

        # Use the processor
        self.worker = worker
        self.root_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.root_dir, "datasets")
        self.save_dir = os.path.join(self.root_dir, "model")

        # Startup Processes
        self.getSaves()

    def getSaves(self):
        """Create a list of Datasets for the selected game."""
        try:
            self.gamesList = os.listdir(self.work_dir)
        except Exception:
            self.print_console(
                "Source path does not exist: {}".format(self.work_dir))
            return

        self.selector.setEnabled(True)
        self.selectingRom = True
        self.actionButton.setEnabled(False)
        self.checkButton.setEnabled(False)
        self.check2Button.setEnabled(False)
        self.currentGame = False
        self.build_selector()

    def selecterator(self):
        """Ensure the finiky QWidget List selector doesnt crash the system."""
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
        self.check2Button.setEnabled(True)
        # click on the button!!!

    def build_selector(self, folder=""):
        """This populates the save folder list."""
        self.selector.clear()
        if not self.selectingRom or folder is not "":
            self.selector.addItem("../")
            for i in sorted(os.listdir(folder)):
                self.selector.addItem("{}".format(i))
        else:
            for i in self.gamesList:
                self.selector.addItem("{}".format(i))

    def show(self):
        """On Show this window."""
        pass

    def hide(self):
        """On hide this window."""
        pass

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Start Training the model."""
        # iters = self.input.text()
        self.print_console("actionButton pressed!")
        self.process.state = 3

    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts."""
        self.print_console("checkButton pressed!")
        self.process.state = 1

    @pyqtSlot()
    def on_check2Button_clicked(self):
        """Test Button for pressing broken parts."""
        self.print_console("check2Button pressed!")
        self.process.state = 2

    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        """Address the selectorator."""
        self.selected = self.selector.selectedItems()
        if len(self.selected) > 0:
            self.selecterator()
            return
        self.actionButton.setEnabled(False)

    @pyqtSlot()
    def closeEvent(self, event=False):
        pass
