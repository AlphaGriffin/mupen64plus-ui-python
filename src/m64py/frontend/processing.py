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

VERSION = sys.version
INTRO = """Create a dataset from saved games.

Select from multiple saves of a single game to create a dataset.
This dataset will be a numpy object (*.npz) in a new folder named
by the title of the game, in a subdir of dataset in your
Mupen64plus save area.
..models/<game_name>/<game_name>_dataset_<num_elements>.npz

Note: Make BW has been disabled. This has been left TODO.
""".format(VERSION,)


class Processing(AGBlank):
    """AG_Trainer Widget of MuPen64 Python Ui."""

    def __init__(self, parent, status, worker, backend):
        super().__init__(parent, status)
        self.setWindowTitle('AG Processing')
        self.selectorLabel.setText('Existing Save Folders:')
        self.selector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.inputLabel.setText('Working Directory(s):')

        self.actionButton.setText('Process')
        self.actionButton.setEnabled(False)
        self.actionButton.setText('Game Select')
        self.checkButton.setEnabled(True)
        self.checkButton.setText('Pick Game')
        self.check2Button.setEnabled(False)
        self.check2Button.setText('Testing')

        self.input.setEnabled(False)
        self.selector.setEnabled(False)

        self.backend = backend
        self.thread = None

        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
        self.selected = None
        self.selection = []
        self.selectedRom = ""
        self.gamePath = ""
        self.selectingRom = True

        self.worker = worker
        self.root_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.root_dir, "training")
        self.save_dir = os.path.join(self.root_dir, "datasets")
        self.getSaves()

    def getSaves(self):
        """Find and list save games."""
        try:
            self.gamesList = os.listdir(self.work_dir)
        except FileNotFoundError:
            self.print_console(
                "Source path does not exist: {}".format(
                    self.work_dir))
            return

        self.selector.setEnabled(True)
        self.selectingRom = True
        self.actionButton.setEnabled(False)
        self.currentGame = False
        self.build_selector()

    def selecterator(self):
        """Set the selector function."""
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
            self.load_dir = os.path.join(self.work_dir, self.currentGame)
            if os.path.isdir(self.load_dir):
                self.print_console("Game Save Dir: {}".format(self.load_dir))
                self.build_selector(folder=self.load_dir)
                return

        # if we need to go back and pick a different game
        if len(select_string) is 3:
            self.print_console("going back to choose another game!")
            self.getSaves()
            return

        # if we have a list of Dirs to work on ...
        self.actionButton.setEnabled(True)
        # click on the button!!!

    def setWorker(self, worker, work_dir=None):
        """Get Worker from main code.

        Check the local Userdata folder.
        """
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.work_dir = os.path.join(self.work_dir, "training")

    def build_selector(self, folder=""):
        """Populate the save folder list."""
        self.selector.clear()
        if not self.selectingRom or folder is not "":
            self.selector.addItem("../")
            for i in sorted(os.listdir(folder)):
                if "." in i:
                    i += '!!!'
                self.selector.addItem("{}".format(i))
        else:
            for i in self.gamesList:
                self.selector.addItem("{}".format(i))

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Process the files."""
        log.debug()
        self.thread = ProcessingThread(self, self.backend, self.selection)
        self.thread.start()

    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts."""
        # reset and select game again...
        self.getSaves()

    @pyqtSlot()
    def on_check2Button_clicked(self):
        """Test Button for pressing broken parts."""
        # reset and select game again...
        pass

    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        """Update the selector."""
        self.selected = self.selector.selectedItems()
        if len(self.selected) > 0:
            self.selecterator()
            return
        self.actionButton.setEnabled(False)


class ProcessingThread(QThread):
    def __init__(self, ui, backend, folders):
        QThread.__init__(self, ui)
        self.ui = ui
        self.backend = backend
        self.folders = folders

    def run(self):
        self.ui.status("Processing...")

        try:
            self.backend.doIt(self.ui.load_dir, self.folders, self.ui.save_dir,
                    self.ui.currentGame)
            self.ui.status("Processing finished.")

        except Exception as e:
            log.error()
            self.ui.status("Error while processing: {}".format(e))

