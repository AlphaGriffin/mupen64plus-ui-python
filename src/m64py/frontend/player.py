# -*- coding: utf-8 -*-
# Author: lannocc @ AlphaGriffin <Alphagriffin.com>
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

import ag.logging as log


#from PIL import Image
VERSION = sys.version

# FIXME
INTRO =\
"""
ARTIFICIAL PLAYER:
        FIXME
""".format(VERSION,)
        
class Player(AGBlank):
    """AG_Player Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        super().__init__(parent)
        self.setWindowTitle('AG Player')
        self.print_console("AlphaGriffin.com - AI Player")

        # model selector (don't populate it until window is actually shown)
        self.selectorLabel.setText('Existing Trained Models:')
        #self.selector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selector.setEnabled(False)

        # play button
        self.actionButton.setText('Play')
        self.actionButton.setEnabled(False)

        # not using checkButton or input (yet)
        self.checkButton.setEnabled(False)
        self.inputLabel.setText('FIXME:')
        self.input.setEnabled(False)
        
        # use the worker
        self.worker = worker
        self.root_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.root_dir, "model")
        
        # status flags
        self.playing = False
        self.selected = None
 
        # all set!
        self.print_console(INTRO)
    
    def show(self):
        """Show this window"""
        super().show()

        if not self.selector.isEnabled():
            self.populateSelector()
            self.selector.setEnabled(True)

        
    def hide(self):
        """Hide this window"""
        super().hide()


    def populateSelector(self, folder=""):
        """This populates the model list"""
        log.debug("populateSelector()")
        self.selector.clear()

        log.debug("about to list files: {}".format(self.work_dir))
        try:
            files = os.listdir(self.work_dir)
            log.debug("files: {}".format(files))

            if files:
                for model in files:
                    self.selector.addItem(model)
            else:
                self.print_console("No models found: {}".format(self.work_dir))
        except FileNotFoundError:
            msg = "model directory not found: {}".format(self.work_dir)
            log.error(msg)
            self.print_console(msg)

           
            
    ###
    ###  UI event handlers
    ###
    
#    @pyqtSlot()
#    def on_actionButton_clicked(self):
#        """Process the files"""
#        self.test = 0
#        #self.processing_()
        
#    @pyqtSlot()
#    def on_checkButton_clicked(self):
#        """Test Button for pressing broken parts"""
#        # reset and select game again...
#        self.test = 0
#        #self.getSaves()
#        #self.print_console(self.selection)
         
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        log.debug("on_selector_itemSelectionChanged()")
        self.selected = None;

        selected = self.selector.selectedItems()
        if len(selected) is 1:
            log.debug("got a selection")
            self.selected = selected[0].text();
            self.actionButton.setEnabled(True)
        
#    @pyqtSlot()
#    def closeEvent(self,event=False):
#        self.test = 0
#        #self.stop()
#        #super().closeEvent()
        
