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
import time
from PyQt5.QtCore import pyqtSlot, QThread
from m64py.frontend.aicommon import AICommon
from m64py.utils import need_dir, version_split
import ag.logging as log

VERSION = sys.version
INTRO =\
    """Recording Console by: AlphaGriffin.com.

    Built in python 3.6
    You are running: {0:2}
    Step 1: Start a ROM, then begin the game and pause it.
    Step 2: If record button does come on, press check.
    Step 3: Press record and go on to enjoy your game.
    Step 4: Move on the next screen for the next step.

    Notes: if you are racing, you can stop the recording
    between races and just click record again and keep playing.
    The more you contribute to the dataset, the better
    you can train your model.
    """.format(VERSION)


class Recorder(AICommon):
    """AG_Recorder Widget of MuPen64 Python Ui."""

    def __init__(self, parent, status, worker, backend):
        """Initialize the interface."""
        super().__init__(parent, status)
        self.setWorker(worker, "training")

        # set up the widgets
        self.setWindowTitle('AG Recorder')
        self.selectorLabel.setText('Existing Save Folders:')
        self.inputLabel.setText('Save to:')
        self.actionButton.setText('Record')
        self.actionButton.setEnabled(False)
        self.checkButton.setEnabled(True)
        self.checkButton.setText('Check')
        self.check2Button.setEnabled(False)
        self.check2Button.setText('unused')
        self.input.setEnabled(False)
        self.selector.setEnabled(False)

        # recording status
        self.recording = False       # are we recording?
        self.recordStartedAt = None  # when did the recording start?
        self.game_on = False         # is there a game runnning?

        # preset some globals
        self.selectedSaveName = None
        self.path = ""
        self.check_game_name = ""
        self.save_name = ""

        # backend and corresponding thread
        self.backend = backend
        self.thread = RecorderThread(self, self.backend)

        # startup
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)

    def set_save_dir(self):
        """Set the input field text."""
        name = self.getGame()
        name_path = os.path.join(self.work_dir, name)
        need_dir(name_path)

        self.print_console("Good Choice with {}, Good luck!".format(name))
        self.build_selector(name_path)

        folder_len = len(os.listdir(name_path))
        path = "newGame_{}".format(folder_len)

        self.input.setText(os.path.join(
            name_path, path
            ))

        self.actionButton.setEnabled(True)

    def build_selector(self, folder):
        """Populate the save folder list."""
        self.selector.clear()
        for i in sorted(os.listdir(folder)):
            listitem = "{}".format(i)
            self.selector.addItem(listitem)
        self.selector.addItem("Record a New Game")

    def getGame(self):
        """Check if game has been selected.

        Set a dir if it has.
        """
        self.check_game_name = self.worker.core.rom_header.Name.decode().replace(
            " ", "_"
            ).lower()
        if self.check_game_name is not "":
            return self.check_game_name
        return "no_game"

    def check_game(self):
        """Check requirements are satisfied to record."""
        self.print_console("Checking Record Readiness.")
        wasloaded = self.game_on

        self.worker.core_state_query(1)
        loaded = self.worker.state in [2, 3]

        ready = False
        if loaded:
            plugins = self.worker.get_plugins()
            pinput = plugins.get(4)
            if not pinput:
                pmap = list(self.worker.core.plugin_map[4].values())[0]
            else:
                pmap = self.worker.core.plugin_map[4][pinput]
            log.debug("detected input plugin", map=pmap)
            pname = pmap[3]
            rname = 'Mupen64Plus SDL Input Plugin - AGE'
            pver = pmap[4]
            rver = int('0x030000', 16)
            self.print_console("Input plugin detected: {} v{}".format(
                    pname, version_split(pver)))
            if pname == rname and pver >= rver:
                ready = True
            else:
                self.print_console("SORRY...input plugin mismatch")
                self.print_console("   required: {} >= v{}".format(
                    rname, version_split(rver)))
                log.error("Wrong input plugin", name=pname,
                        version=version_split(pver), required_name=rname,
                        required_version=version_split(rver))

        self.game_on = loaded and ready

        if self.game_on:
            if wasloaded:
                self.actionButton.setEnabled(False)
            if self.recording:
                self.stop()

        if not wasloaded:
            if self.game_on:
                self.set_save_dir()

    def record(self):
        """Start the recording timer and action functions."""
        self.status("Recording...")
        self.print_console("Starting Recording")
        self.actionButton.setText('Stop')

        self.save_name = self.input.text()
        need_dir(self.save_name)

        msg = "Ready to Save in Directory: {}".format(self.save_name)
        self.print_console(msg)

        if self.thread.isRunning():
            log.warn("not ready yet")
            return

        self.backend.root_dir = self.root_dir
        self.backend.save_name = self.save_name
        self.worker.ai_record()
        self.recording = True
        self.recordStartedAt = time.time()*1000.0

    def stop(self):
        """End the recording session.

        Also buttons up the screenshot dir.
        """
        if self.recording:
            self.status("Done recording.")
            # self.poll_time.stop()
            self.worker.ai_stop()
            self.actionButton.setText('Record')

            elapsed = time.time()*1000.0 - self.recordStartedAt
            self.print_console("Recording took {} seconds".format(elapsed/1000.0))
            self.recordStartedAt = None

            self.set_save_dir()
            self.recording = False

            self.thread.start()

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Start, stop record button."""
        if not self.recording:
            self.record()
        else:
            self.stop()

    @pyqtSlot()
    def on_checkButton_clicked(self):
        """check constitution of system."""
        self.check_game()

    @pyqtSlot()
    def on_check2Button_clicked(self):
        """Test Button for pressing broken parts."""
        pass

    @pyqtSlot()
    def on_selector_itemSelectionChanged(self): pass


class RecorderThread(QThread):
    def __init__(self, ui, backend):
        QThread.__init__(self, ui)
        self.ui = ui
        self.backend = backend

    def run(self):
        self.ui.status("Finalizing Recording...")

        try:
            self.backend.get_controllers()
            self.backend.get_images()
            self.ui.status("Recording finished.")

        except Exception as e:
            log.error()
            self.ui.status("Error while finishing recording: {}".format(e))

