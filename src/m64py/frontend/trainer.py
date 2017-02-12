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
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import pyqtSlot#, QTimer
from PyQt5.QtWidgets import QAbstractItemView
import os, sys#, time, shutil
from glob import glob as check
import pandas as pd
VERSION = sys.version

# FIXME
INTRO =\
"""
TRAINING AND CONVERSION SOFTWARE:
        Select from multiple saves of a single game to create a dataset. This
        dataset will need to be converted to a proper image size and coloring.
        Then the dataset needs to be split into training, testing and 
        validation sets. From there a model can be created with the use of a 
        single opimization pass with random settings to create and save your 
        model. At this point you can take your model and optimization function
        to AWS and pay the 5 cents to run your model for an hour or 2. Ill need
        to add instructions for that. Unless you have sufficent graphics card
        to try and train it on your machine.
        
        Step one. Pick multiple files from a single game.
        Step Two. Batch Convert images and create a running numpy object(3d) of
        2d arrays. Save That and the controller input(label) as Input:label for
        your dataset.
        Step Three. Split the dataset into 3 different single object python
        dictionaries, which are Input:label for Train, test, and verifcation.
        Step Four. Verify the shit out of previous steps and create and save a
        model with a single optimization.
        Step Five. Training a dataset is a matter of running through every
        image in the training set and optimizing the necessary weights and
        balances for the model to correctly give a label to an image.
""".format(VERSION,)

class Process(object):
    def __init__(self):
        self.test = 1
                
    def gamepadImageMatcher(path):
        #INFO = "SAW -- matches gamepad csv data rows to images based on timestamps\nReturns two matching arrays"
	
    	  # Open CSV for reading
        csv_path = os.path.join(path, "data.csv")
        print("about to open: {}".format(csv_path))
        csv_io = open(csv_path, 'r')
        print ("csv successfully opened")
        
        # Convert to a true array
        csv = []
        for line in csv_io:
            # Split the string into array and trim off any whitespace/newlines in elements
            csv.append([item.strip() for item in line.split(',')])
        if not csv:
            print ("CSV HAS NO DATA")
            return None, None
            
        # Get list of images in directory and sort it
        all_files = os.listdir(path)
        print ("all_files: {}".format(all_files))
        #images = [image for image in all_files if any(image.endswith('.png'))]
        images = []
        for filename in all_files:
            if filename.endswith('.png'):
                images.append(filename)
        images = sorted(images)
        print ("sorted images list: {}".format(images))
        
        if not images:
            print ("FOUND NO IMAGES");
            return None, None
    
        # We're going to build up 2 arrays of matching size:
        keep_csv = []
        keep_images = []
    	
        # Prime the pump (queue)...
        prev_line = csv.pop(0)
        prev_csvtime = int(prev_line[0])
        print ("line 0: {}".format(prev_line))
    	
        #prev_image = images[0]
        #prev_imgtime = 0
    	
        # Find next matching image
        while images:
            imgfile = images[0]
            print ("imgfile: {}".format(imgfile))
    		 # Get image time:
    		 #     Cut off the "gamename-" from the front and the ".png" from the end
            hyphen = imgfile.rfind('-') # Get last index of '-'
            if hyphen < 0:
                print ("UNEXPECTED FILENAME, ABORTING: {}".format(imgfile))
                break
            imgtime = int(imgfile[hyphen+1:-4]) # cut it out!
            print ("imgtime: {}".format(imgtime))
            lastKeptWasImage = False # Did we last keep an image, or a line?
            if imgtime > prev_csvtime:
                print ("keeping image: {}".format(imgtime))
                keep_images.append(imgfile)
                del images[0]
                lastKeptWasImage = True
                
                
                # We just kept an image, so we need to keep a
                #corresponding input row too
                while csv:
                    line = csv.pop(0)
                    print ("line: {}".format(line))
                    csvtime = int(line[0])
                    print ("csvtime: {}".format(str(csvtime)))
    				
                    if csvtime >= imgtime:
                        # We overshot the input queue... ready to
                        # keep the previous data line
                        print ("keeping line: {}".format(prev_csvtime))
                        keep_csv.append(prev_line)
                        lastKeptWasImage = False
    					
                        prev_line = line
                        prev_csvtime = csvtime
    				
                        if csvtime >= imgtime:
                            break;
    					
                    if not csv:
                        print ("OUT OF CSV DATA")
                        if lastKeptWasImage:
                            print ("keeping line: {}".format(prev_csvtime))
                            keep_csv.append(prev_line)
                        break
    				
                else:
                    print ("dropping image: {}".format(imgtime))
                    del images[0]
    		
        print ("len(keep_data): {}".format(len(keep_csv)))
        print ("len(keep_images): {}".format(len(keep_images)))
        #self.print_console("MATCHED RESULTS COUNT: {} <--> {}".format(len(keep_csv),len(keep_images)))
        return keep_csv, keep_images

        
        
class Trainer(AGBlank):
    """AG_Trainer Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        super().__init__(parent)
        self.setWindowTitle('AG Trainer')
        self.selectorLabel.setText('Existing Save Folders:')
        
        self.selector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.selector.setSelectionMode(QAbstractItemView.MultiSelection)
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
        self.selectedRom = ""
        self.selectingRom = True
        
        # Use the processor
        self.processor = Process()
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.work_dir, "training")
        
        self.getSaves()
        
        
    """ TEST FUNCTIONS """
    def getSaves(self):
        """
        This should comb the workdir and put together some stats.
        GameName : Amount of saves : ??
        """
        self.gamesList = os.listdir(self.work_dir)
        #self.print_console("Games Played:\n" + "\n".join(x for x in self.gamesList))
        #self.build_selector(self.work_dir)
        self.selector.setEnabled(True)
        self.selectingRom = True
        self.actionButton.setEnabled(False)
        self.currentGame = False
        self.build_selector()
        
    def selection(self):
        selection = []
        for x in self.selected:
            selection.append(x.text())
        select_string = ", ".join(x for x in selection)
        self.print_console(select_string)
        
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
    def print_console(self, msg): 
        """Takes a String and prints to console"""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText("{}\n".format(msg))
        #print(msg)
        
    def setWorker(self, worker):
        """Get Worker(ref) from main code and check the local Userdata folder"""
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.work_dir, "training")

    def check_tail(self, path):
        """Read and print from the CSV file if it exists"""
        x = '{}/{}/data.csv'.format(self.work_dir,path)
        if check(x):
            df = pd.read_csv(x)
            top = df.head(5)
            bottom = df.tail(10)
            concatenated = pd.concat([top,bottom])
            self.print_console("This looks like an Unprocessed Folder\n{}\nRecord in another Dir".format(concatenated))
        else:
            self.print_console("file!=\t{}\nNo Previous Save in this Directory\n\tGame ON!".format(x))
            
    def build_selector(self, folder=""):
        """This populates the save folder list"""
        self.selector.clear()
        if not self.selectingRom or folder is not "": 
            self.selector.addItem("../")
            x = sorted(os.listdir(folder))
            for i in x:
                #print(i)
                self.selector.addItem("{}".format(i))   
        else:
            for i in self.gamesList:
                self.selector.addItem("{}".format(i))
        # then we need to be selecting folders to process
                    
            
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
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        self.getSaves()
         
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        self.selected = self.selector.selectedItems()
        #self.print_console(self.selected)
        #for x in self.selected: self.print_console(x.text()) # good test!
        
        # protect deselect... for gods sake...
        if len(self.selected) > 0:
            self.selection()
            return
        self.actionButton.setEnabled(False)
        
    @pyqtSlot()
    def closeEvent(self,event=False):
        self.test = 0
        #self.stop()
        #super().closeEvent()
        