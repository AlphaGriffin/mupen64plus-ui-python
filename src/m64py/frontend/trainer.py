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
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QAbstractItemView
from m64py.frontend.agblank import AGBlank
import ag.logging as log

pyVERSION = sys.version
INTRO = """Model Creation and Training SOFTWARE using TensorFlow.
    Python Version: {}
    Step 1 - Choose a Dataset.

    Step 2 - Click Train New Model. Visit AlphaGriffin.com for other ways and
    tools to train models. Make sure to Train at least 1 iteration and save
    the model.

    Step 3  - Then either (1) Load and Optimize your existing model or
    (2) take the model to Alphagriffin.com or your own AWS for further
    optimization.
""".format(pyVERSION)


class Trainer(AGBlank):
    """Give the user some control over the AI training."""

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
        self.process = Training(self)
        self.process.start()

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
        self.input.setText("100")  # FIXME?
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

