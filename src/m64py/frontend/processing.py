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
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QAbstractItemView
import os, sys
import numpy as np
from PIL import Image
VERSION = sys.version

INTRO =\
"""
CONVERSION SOFTWARE:
        Select from multiple saves of a single game to create a dataset. This 
        dataset will consist of 2 numpy objects (*.npy) in a new folder named 
        by the title of the game, in a subdir of dataset in your Mupen64plus
        save area.
        
        ** note: Make BW has been disabled. because BW would also have to be
        implemented in playback. This adds an extra step and is left TODO at
        release.
""".format(VERSION,)

class Prepare(object):
    """ 
    This will be used by both the Process and Playback Modules for conversion
    of images for Tensorflow.
    """
    def __init__(self,options=None):
        self.options = options
                
    def make_BW(self,rgb):
        """ This is the "rec601 luma" algorithm to compute 8-bit greyscale """
        return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
    
    def prepare_image(self, img, makeBW=False):
        """ This resizes the image to a tensorflowish size """
        pil_image = Image.open(img)                       # open img
        x = pil_image.resize((200, 66), Image.ANTIALIAS)  # resizes image
        numpy_img = np.array(x)                           # convert to numpy 
        if makeBW:  
            numpy_img = self.make_BW(numpy_img)           # grayscale
        return numpy_img
        
    def gamepadImageMatcher(self, path):
        """
        - SAW - matches gamepad csv data rows to images based on timestamps
        Params: A path with timestamped pictures and a ti1estamped .csv of
                different lenghs.
        Returns: two arrays of matched length img, labels.
        """
                
        # Open CSV for reading
        csv_path = os.path.join(path, "data.csv")
        csv_io = open(csv_path, 'r')
        
        # Convert to a true array
        csv = []
        for line in csv_io:
            # Split the string into array and trim off any whitespace/newlines
            csv.append([item.strip() for item in line.split(',')])
        if not csv:
            #print ("CSV HAS NO DATA")
            return None, None
            
        # Get list of images in directory and sort it
        all_files = os.listdir(path)
        images = []
        for filename in all_files:
            if filename.endswith('.png'):
                images.append(filename)
        images = sorted(images)
        
        if not images:
            #print ("FOUND NO IMAGES");
            return None, None
    
        # We're going to build up 2 arrays of matching size:
        keep_csv = []
        keep_images = []
    
        # Prime the pump (queue)...
        prev_line = csv.pop(0)
        prev_csvtime = int(prev_line[0])
    
        while images:
            imgfile = images[0]
            # Get image time:
            #     Cut off the "gamename-" from the front and the ".png"
            hyphen = imgfile.rfind('-') # Get last index of '-'
            if hyphen < 0:
                break
            imgtime = int(imgfile[hyphen+1:-4]) # cut it out!
            lastKeptWasImage = False # Did we last keep an image, or a line?
            if imgtime > prev_csvtime:
                keep_images.append(imgfile)
                del images[0]
                lastKeptWasImage = True
                
                # We just kept an image, so we need to keep a
                #corresponding input row too
                while csv:
                    line = csv.pop(0)
                    csvtime = int(line[0])
    
                    if csvtime >= imgtime:
                        # We overshot the input queue... ready to
                        # keep the previous data line
                        # truncate  the timestamp
                        keep_csv.append(prev_line[1:]) 
                        lastKeptWasImage = False
    
                        prev_line = line
                        prev_csvtime = csvtime
    
                        if csvtime >= imgtime:
                            break;
    
                    if not csv:
                        if lastKeptWasImage:
                            # truncate off the timestamp
                            keep_csv.append(prev_line[1:]) 
                        break
    
            else:
                del images[0]
        return keep_csv, keep_images

        
        
class Processing(AGBlank):
    """AG_Trainer Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        super().__init__(parent)
        self.setWindowTitle('AG Processing')
        self.selectorLabel.setText('Existing Save Folders:')
        self.selector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.inputLabel.setText('Working Directory(s):')
        self.actionButton.setText('Process')
        self.actionButton.setEnabled(False)
        self.actionButton.setText('Game Select')
        self.checkButton.setEnabled(True)
        self.checkButton.setText('Pick Game')
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
        self.process = Prepare()
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.root_dir = self.work_dir
        self.work_dir = os.path.join(self.work_dir, "training")
        self.getSaves()
        
        
    """ TEST FUNCTIONS """
    def processing_(self, folders=""):
        """This has 3 steps, move files, convert images, create bins"""
        # this should be global but its breaking!
        proc = Prepare()
        if folders is "": 
            folders = self.selection
        saveDir = os.path.join(self.root_dir, "datasets", self.currentGame)
        if not os.path.isdir(saveDir):
            self.print_console("Creating folder: {}".format(saveDir))
            os.mkdir(saveDir)
        datasetIndex = len(os.listdir(saveDir))
        dataset_x = []
        dataset_y = []
        datasetFilename = "{}_dataset_{}".format(self.currentGame,datasetIndex)
        self.print_console("#############################################")
        self.print_console("# Processing Game folders to dataset")
        self.print_console("# Game Name: {}".format(self.currentGame))
        self.print_console("# Dataset Path: {}".format(saveDir))
        self.print_console("# Number of saves to process: {}".format(
                           len(folders)))
        self.print_console("#############################################")
        
        # for each folder given...
        for i in folders:
            current_path = os.path.join(self.work_dir,self.currentGame,i)
            self.print_console("# Processing folder: {}".format(current_path))
            self.print_console("# Step 1: Assert #imgs == #labels")
            labels, imgs = proc.gamepadImageMatcher(current_path)
            dataset_y.append(labels) # BOOM!
            self.print_console("# Step 2: Convert img to BW np array of (x,y)")
            for image in imgs:
                img = proc.prepare_image(os.path.join(current_path,image))
                dataset_x.append(img)
        
        self.print_console("# Step 3: Save files...\n\t{}.npz".format(datasetFilename))
        dataset_x = np.asarray(dataset_x)
        dataset_y = np.concatenate(dataset_y)
        # super_set = [dataset_x, dataset_y]
        self.print_console("# To Dir:\t{}".format(saveDir))
        # np.save(os.path.join(saveDir, datasetFilename_x), dataset_x)
        # np.save(os.path.join(saveDir, datasetFilename_y), dataset_y)
        np.savez(os.path.join(saveDir, datasetFilename), images=dataset_x, labels=dataset_y)
        self.print_console("# Finished preparing dataset")
        
    
    """ Selector FUNCTIONS """
    def getSaves(self):
        """
        Creates a list of Games that have saves and resets the selected game.
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
        self.actionButton.setEnabled(True)
        # click on the button!!!
        
    def setWorker(self, worker):
        """Get Worker from main code and check the local Userdata folder"""
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
                    
    def show(self):
        """On Show this window"""
        super().show()
        
    def hide(self):
        """On hide this window"""
        super().hide()
    
    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Process the files"""
        self.processing_()
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        # reset and select game again...
        self.getSaves()
         
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        self.selected = self.selector.selectedItems()
        if len(self.selected) > 0:
            self.selecterator()
            return
        self.actionButton.setEnabled(False)
        
    @pyqtSlot()
    def closeEvent(self,event=False): pass