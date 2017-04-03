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
from PyQt5.QtCore import pyqtSlot, QTimer
import os, sys, pygame, time, shutil

import ag.logging as log

VERSION = sys.version

# FIXME
INTRO =\
"""
Recording Console by: AlphaGriffin.com
Built in python 3.5.2
You are running: {0:2}
Step 1: Start a ROM and get past the menus and into the game and pause it.
Step 2: press the check if game is running button for non-async...
Step 3: Press record and go on to enjoy your game.
Step 4: When you exit out of the game the Recording will automatically stop.
step 5: Move on to the Processing Console.

Notes: if you are racing, you can stop the recording between races and just click
record again and keep playing. The more you contribute to the dataset, the
better you can train your model.
""".format(VERSION)

class xpad(object):
    """ This conversion comes from the orginal TKart Demo """
    def __init__(self,options=None):
        try:
            self.joystick.init()
        except:
            print('unable to connect to Xbox Controller')
            
    def read(self):
        """ This is the call polled for the xpad data """
        pygame.event.pump()
        # left stick
        L_x_axis = self.joystick.get_axis(0)
        L_y_axis = self.joystick.get_axis(1)
        # need left stick click
        # right stick
        # R_x_axis = self.joystick.get_axis(2)
        # R_y_axis = self.joystick.get_axis(3)
        # need right stick click
        # need d-pad

        # game buttons
        a_btn = self.joystick.get_button(1) ## HACKS!! THIS A HACK
        b_btn = self.joystick.get_button(2) ## THESE buttons are re maped in the thing... /hack
        # x_btn = self.joystick.get_button(2)
        # y_btn = self.joystick.get_button(3)
        
        # top buttons
        # lb = self.joystick.get_button(4)
        rb = self.joystick.get_button(5)

        # need start / select

        # need triggers /
        return [L_x_axis, L_y_axis, a_btn, b_btn, rb]
        
    def manual_override(self):
        """ This takes over from the AI, allows for better 2nd Gen Training """
        pygame.event.pump()
        return self.joystick.get_button(4) == 1
        
        
class Recorder(AGBlank):
    """AG_Recorder Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        log.debug("Recorder::__init__()")
        # init
        super().__init__(parent)
        self.setWorker(worker)   # get this from MUPEN core
        self.pad = xpad()        # get a controller instance
        
        # set up the blanks
        self.setWindowTitle('AG Recorder')
        self.selectorLabel.setText('Existing Save Folders:')
        self.inputLabel.setText('Save to:')
        self.actionButton.setText('Record')
        self.actionButton.setEnabled(False)
        self.checkButton.setEnabled(True)
        self.input.setEnabled(False)
        self.selector.setEnabled(False)
        
        # timer state
        self.runningTimer = False
        
        # booleans are good
        self.recording = False       # are we recording?
        self.recordStartedAt = None  # when did the recording start?
        self.game_on = False         # is there a game runnning?
        
        # preset some globals
        self.selectedSaveName = None
        self.path = ""
        self.check_game_name = ""
        
        # startup
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
              

    def set_save_dir(self):
        """Sets the Input Field text"""
        name = self.getGame()
        name_path = os.path.join(self.work_dir, "training", name)
        if not os.path.isdir(name_path):
            print ("path does not exist, creating it now: {}".format(
                   name_path))
            os.makedirs(name_path)
        self.print_console("Good Choice with {}, Good luck!".format(name))
        
        self.build_selector(name_path)
        
        l = len(os.listdir(name_path))
        path = "newGame_{}".format(l)
        self.input.setText(os.path.join(name_path,path))
        self.actionButton.setEnabled(True)
        
    def build_selector(self, folder):
        """This populates the save folder list"""
        self.selector.clear()
        for i in sorted(os.listdir(folder)):
            x = "{}".format(i)
            self.selector.addItem(x)
        self.selector.addItem("Record a New Game")
        
    def save_data(self,test=False):
        """
        Create data.csv - Timestamp, { 0.0, 0.0, 0, 0, 0 }
        """
        paddle_read = self.pad.read()
        stamp = int(time.time() * 1000)
        y = ("{}:\t{}".format(stamp,paddle_read))
        if test is False:
            # make / open outfile
            outfileName = os.path.join(self.save_name, 'data.csv')
            print("".format(outfileName))
            outfile = open(outfileName, 'a')
            
            # write line
            outfile.write('{},{}\n'.format(stamp, ','.join(
                          map(str, paddle_read))))
            outfile.close()
        self.print_console(y)
        
    #def setWorker(self, worker):
    #    """Get Worker from main code and check the local Userdata folder"""
    #    self.worker = worker
    #    self.work_dir = self.worker.core.config.get_path("UserData")
        
    def getGame(self):
        """Check if game has been selected and set a dir if it has"""
        x = self.check_game_name = self.worker.core.rom_header.Name.decode().replace(" ", "_").lower()
        if x is not "":
            return x
        return "no_game"
               
    def startupTimer(self):
        """Start a timer if none is running and keep checking back"""
        # start game checker
        if self.runningTimer == False:
            self.print_console("Start a Game to begin, dont record til you are in gameplay")
            self.runningTimer = QTimer(self)
            self.runningTimer.timeout.connect(self.check_game) # takes the pick and saves data
            self.runningTimer.start(200)    # in millis
                 
    def shutdownTimer(self):
        """Shuts down the timer when we don't need it (dialog hidden, etc.)"""
        if not self.runningTimer == False:
            self.runningTimer.stop()
            self.runningTimer = False
            
            
    def check_game(self):
        """Check mupen worker and see if hes working, called by runningTimer"""
        wasloaded = self.game_on
        self.worker.core_state_query(1)
        loaded = self.worker.state in [2, 3]
        self.game_on = loaded
        
        if not loaded:
            if wasloaded:
                self.actionButton.setEnabled(False)
            if self.recording:
                self.stop()
        
        if not wasloaded:
            if loaded:
                self.set_save_dir()       
    
        
    def record(self):
        """this starts the recording timer and actionable function"""
        self.actionButton.setText('Stop')
        self.save_name = self.input.text()
        
        if not os.path.isdir(self.save_name):
            os.makedirs(self.save_name)
        
        self.poll_time = QTimer(self)
        self.poll_time.timeout.connect(self.save_data) # takes the pick and saves data
        self.poll_time.start(50)    # in millis
        self.worker.toggle_autoshots()
        self.recording = True
        self.recordStartedAt = time.time()*1000.0
        
    def stop(self):
        """This ends the recording session and buttons up the screenshot dir"""
        if self.recording:
            self.poll_time.stop()
            self.worker.toggle_autoshots()
            self.actionButton.setText('Record')
            
            elapsed = time.time()*1000.0 - self.recordStartedAt
            self.print_console("Recording took {} seconds".format(elapsed/1000.0))
            self.recordStartedAt = None
            
            self.set_save_dir()
            self.recording = False
            self.get_images()
        
    def get_images(self):
        """This moves all the screenshots to the current save_dir"""
        print ("in get_images()")
        shot_dir = os.path.join(self.work_dir,"screenshot/")
        print ("about to list dir: {}".format(shot_dir))
        x = os.listdir(shot_dir)
        print ("got stuff: {}".format(x))
        if len(x) > 0:
            y = []
            for i in x:
                y.append(i)
                #print(shot_dir+i)
                
                mv_from = os.path.join(shot_dir, i)
                mv_to = self.save_name
                print ("moving: {} -> {}".format(mv_from, mv_to))
                shutil.move(mv_from, mv_to)
            
            self.print_console("Got {} images, moved to {}".format(len(y),self.save_name))
            
        else:
            self.checkButton.setEnabled(True)
            self.print_console("No ScreenShots Saved")
            
    def show(self):
        """ default show command """
        self.startupTimer()
        super().show()
        
    def hide(self):
        """ This stops recording on game close """
        self.shutdownTimer()
        self.stop()
        super().hide()

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Start - Stop record button"""
        if not self.recording: self.record()
        else: self.stop()
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        self.check_game()
     
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self): pass
        
    @pyqtSlot()
    def closeEvent(self,event=False): pass
