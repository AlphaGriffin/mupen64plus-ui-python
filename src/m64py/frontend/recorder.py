# -*- coding: utf-8 -*-
# Author: SAW @ AlphaGriffin <Alphagriffin.com>
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
from m64py.core.defs import *
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import pyqtSlot, QTimer
import time
import pygame
import os, sys
from glob import glob as check
import pandas as pd
#from m64py.core.core import Core
from m64py.utils import sl
VERSION = sys.version

INTRO =\
"""
Recording Console by: AlphaGriffin.com GNU3
Built in python 3.5.2\n
You are running: {0:2}\n
Step 1: Start a Game and Pause it.\n
Step 2: Press the Check Button and Get the Game Creds\n
Step 3: Choose New Game and Press record\n
step 4: Play just 1 round of your game, pause it, then come back and stop your recording.\n\n\n\n
Start here
 |
 |
 |
\ /
""".format(VERSION,)

class xpad(object):
    def __init__(self,options=None):
        try:
            pygame.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        except:
            print('unable to connect to Xbox Controller')
    def read(self):
        pygame.event.pump()
        L_x_axis = self.joystick.get_axis(0)
        L_y_axis = self.joystick.get_axis(1)
        a_btn = self.joystick.get_button(1)
        b_btn = self.joystick.get_button(2)
        # top buttons
        rb = self.joystick.get_button(5)
        return [L_x_axis, L_y_axis, a_btn, b_btn, rb]
    def manual_override(self):
        pygame.event.pump()
        return self.joystick.get_button(4) == 1
        
class Recorder(AGBlank):
    """AG_Recorder Widget of MuPen64 Python Ui"""
    def __init__(self, parent=None, worker=None, core=None):
        # init
        super().__init__()
        self.pad = xpad()
        # set up the blanks
        self.setWindowTitle('AG Recorder')
        self.selectorLabel.setText('Existing Save Folders:')
        self.inputLabel.setText('Save to:')
        self.actionButton.setText('Record')
        self.actionButton.setEnabled(False)
        # booleans are good
        self.recording = False
        # preset some globals
        self.selectedSaveName = None
        self.path = ""
        self.work_dir = "/tmp"
        self.check_game_name = ""
        # startup
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
        
    def show(self):
        self.refresh()
        super().show()
        

    def populate_selector(self):
        self.selector.clear()
        self.work_dir = self.worker.core.config.get_path("UserData")
        print ("work_dir: {}".format(self.work_dir))
        self.check_game_name = self.worker.core.rom_header.Name.decode().replace(" ", "_").lower()
        print ("check_game_name: {}".format(self.check_game_name))
        path = self.work_dir + "/" + self.check_game_name
        print ("path: {}".format(path))
        
        for i in os.listdir(path):
            x = "{}".format(i)
            self.selector.addItem(x)
            
        self.selector.addItem("__New_Game__")
        
    
    def save_data(self):
        # screen shots go to a preset place
        self.worker.save_screenshot()
        # make / open outfile
        outfile = open(self.outputDir+'/'+'data.csv', 'a')
        # write line
        outfile.write( '{},'.format(int(time.time() * 1000)) + ','.join(map(str, self.controller_data)) + '\n' )
        outfile.close()
        
    def update_(self):
        x = self.pad.read()
        stamp = int(time.time() * 1000)
        y = ("{}:\t{}".format(stamp,x))
        self.print_console(y)
        return True
    
    def print_console(self, msg): 
        """Takes a String and prints to console"""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText("{}\n".format(msg))
    
    
    def set_save_dir(self,path):
        self.input.setText(path)
        
    def check_tail(self, path):
        x = '{}/{}/data.csv'.format(self.path,path)
        if check(x):
            df = pd.read_csv(x)
            top = df.head(5)
            bottom = df.tail(10)
            concatenated = pd.concat([top,bottom])
            self.print_console("This looks like an Unprocessed Folder\n{}\nRecord in another Dir".format(concatenated))
        else:
            self.print_console("file!=\t{}\nNo Previous Save in this Directory\n\tGame ON!".format(x))
            
        
    def setWorker(self, worker):
        self.worker = worker
        
        
    def check_worker(self): 
        
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.check_game_name = self.worker.core.rom_header.Name.decode().replace(" ", "_").lower()
        d = os.listdir(self.work_dir)
        self.populate_selector(d)
        
    def refresh(self):
        print ("refreshing state")
        loaded = False
        self.worker.core_state_query(M64CORE_EMU_STATE)
        loaded = self.worker.state in [M64EMU_RUNNING, M64EMU_PAUSED]
        print ("game loaded: {}".format(loaded))
        #selected = loaded and selected
        self.selector.setEnabled(loaded)
        
        if loaded:
            self.populate_selector()
        
    def Check_game_stats(self):
        self.worker.core_state_query(M64CORE_EMU_STATE)
        if self.worker.state in [M64EMU_RUNNING, M64EMU_PAUSED]:
            self.check_worker()
        if self.check_game_name is not "":
            self.work_dir = os.path.join(self.work_dir,self.check_game_name)
        self.print_console(self.work_dir)
        
        
    def get_images(self,):
        self.worker.get_screenshot()
        
    def record(self):
        self.actionButton.setText('Stop')
        save_name = self.input.text()
        
        if save_name == '__New_Game__' or '':
            save_name = "{}".format(int(time.time() * 1000))
        self.print_console("save name: {}".format(save_name))
        
        save_path = "{}/{}/{}".format(self.path, self.selectedSaveName, save_name)
        self.print_console("save full path: {}".format(save_path))
        
        self.poll_time = QTimer(self)
        self.poll_time.timeout.connect(self.update_) # takes the pick and saves data
        self.poll_time.start(200)    # in millis
        #self.worker.toggle_autoshots()
        self.recording = True
        
    def stop(self):
        self.actionButton.setText('Record')
        self.worker.toggle_autoshots()
        self.poll_time.stop()
        self.recording = False

        
    def on_stop_finish(self,): 
        screen_shot_dir = 0
        # copys the screenshot dir to the working dir
        # asset len(csv) == len(#pics)
        # copy data.csv to img folder and name it properly
        
    @pyqtSlot()
    def on_actionButton_clicked(self):
        if not self.recording:
            
            self.record()
        else:
            self.stop()
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        #self.Check_game_stats()
        self.refresh()
            
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        selected = self.selector.selectedItems()
        self.inputLabel.setText(selected)
        self.selectedSaveName = selected[0].text()
        #self.check_tail(self.selectedSaveName)
        # our UI enforces that only one item is selected...
        if selected is not None and len(selected) > 0:
            self.actionButton.setEnabled(True)
            self.set_save_dir(self.selectedSaveName) # set the text box to this name
        else:
            self.actionButton.setEnabled(False)

# We are keeping a persistent object around... may or may not be a good idea:
recorder = Recorder()