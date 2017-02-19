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
from PyQt5.QtCore import pyqtSlot#, QTimer
from PyQt5.QtWidgets import QAbstractItemView
import os, sys#, time, shutil
#from glob import glob as check
#import pandas as pd
import numpy as np

#import lib.build_network as net         # Plug all the data into Tensorflow... very carefully...
#import lib.process_network as proc      # Actually run the TF machine


#from PIL import Image
VERSION = sys.version

# FIXME
INTRO =\
"""
Tensorflow Model Creation and Training SOFTWARE:
    
    Step 1 - Choose a Dataset.
    
    Step 2 -

""".format(VERSION,)
        
class OUTTFSHIT_HERE(object):
    def __init__(self): pass

    def BATCH_SHIT(self):pass

    def DATASPLIT_SHIT(self): pass

    def LOAD_NUMPY_DATASET(self): pass
        
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
        self.actionButton.setText('Game Select')
        self.checkButton.setEnabled(True)
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
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.root_dir = self.work_dir
        self.work_dir = os.path.join(self.work_dir, "training")
        
        self.getSaves()
        
        
    """ TEST FUNCTIONS """
    def processing_(self, folders=""):
        """This has 3 steps, move files, convert images, create bins"""
        
        # this should be global but its breaking!
        
        if folders is "": 
            folders = self.selection
        saveDir = os.path.join(self.root_dir, "datasets", self.currentGame)
        if not os.path.isdir(saveDir):
            self.print_console("Creating folder: {}".format(saveDir))
            os.mkdir(saveDir)
        datasetIndex = len(os.listdir(saveDir))
        dataset_x = []
        dataset_y = []
        datasetFilename_x = "_{}_dataset_{}_image.npy".format(self.currentGame,datasetIndex)
        datasetFilename_y = "_{}_dataset_{}_label.npy".format(self.currentGame,datasetIndex)
        self.print_console("#############################################")
        self.print_console("# Processing Game folders to dataset")
        self.print_console("# Game Name: {}".format(self.currentGame))
        self.print_console("# Dataset Path: {}".format(saveDir))
        self.print_console("# Number of saves to process: {}".format(len(folders)))
        self.print_console("#############################################")
        
        # for each folder given...
        for i in folders:
            current_path = os.path.join(self.work_dir,self.currentGame,i)
            self.print_console("# Processing folder: {}".format(current_path))
            self.print_console("# Step 1: Assert #imgs == #labels")
            labels, imgs = self.proc.gamepadImageMatcher(current_path)
            
            #self.print_console("# DEBUGS!!! - 1")
            # labels first, cause why?? easier i guess...
            dataset_y.append(labels) # BOOM!
            self.print_console("# Debugs!! 1")
            # then images... cause... f the dang...
            self.print_console("# Step 2: Convert img to BW np array of (x,y)")
            for image in imgs:
                self.print_console(os.path.join(current_path,image))
                img = self.proc.prepare_image(os.path.join(current_path,image)) # process the image
                dataset_x.append(img)
        
        self.print_console("# Step 3: Save files...\n\t{}\n\t{}".format(
                           datasetFilename_x, datasetFilename_y))
        dataset_x = np.asarray(dataset_x)
        dataset_y = np.concatenate(dataset_y)
        self.print_console("# To Dir:\t{}".format(saveDir))
        np.save(os.path.join(saveDir, datasetFilename_x), dataset_x)
        np.save(os.path.join(saveDir, datasetFilename_y), dataset_y)
        self.print_console("# Finished preparing dataset")
        
    
    """ Selector FUNCTIONS """
    def getSaves(self):
        """
        Creates a list of Games that have saves and resets the selected game.
        """
        try:
            self.gamesList = os.listdir(self.work_dir)
        except FileNotFoundError:
            self.print_console("Source path does not exist: {}".format(self.work_dir))
            return

        self.selector.setEnabled(True)
        self.selectingRom = True
        self.actionButton.setEnabled(False)
        self.currentGame = False
        self.build_selector()
        
    def selecterator(self):
        selection = []
        for x in self.selected:
            selection.append(x.text())
        select_string = ", ".join(x for x in selection)
        self.print_console(select_string)
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
        self.actionButton.setEnabled(True)
        # click on the button!!!
        
    """ EASY GOOD WORKING FUNC's """
    def setWorker(self, worker):
        """Get Worker(ref) from main code and check the local Userdata folder"""
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.work_dir, "training")
           
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
                    
            
    ###
    ###  These Slots are set in the UI designer and need to be reset here
    ###
    
    def show(self):
        """On Show this window"""
        super().show()
        
    def hide(self):
        """On hide this window"""
        super().hide()
    
    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Process the files"""
        self.test = 0
        #self.processing_()
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        # reset and select game again...
        self.test = 0
        #self.getSaves()
        #self.print_console(self.selection)
         
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        self.selected = self.selector.selectedItems()
        self.print_console(self.selected)
        for x in self.selected: self.print_console(x.text()) # good test!
        
        # protect deselect... for gods sake...
        #if len(self.selected) > 0:
        #    self.selecterator()
        #    return
        #self.actionButton.setEnabled(False)
        
    @pyqtSlot()
    def closeEvent(self,event=False):
        self.test = 0
        #self.stop()
        #super().closeEvent()
        
