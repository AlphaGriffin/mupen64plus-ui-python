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
import time
import shutil
from PyQt5.QtCore import pyqtSlot
from m64py.frontend.agblank import AGBlank
from m64py.utils import version_split
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


class Recorder(AGBlank):
    """AG_Recorder Widget of MuPen64 Python Ui."""

    def __init__(self, parent, status, worker):
        """Set global references."""
        log.debug()
        # init
        super().__init__(parent, status)
        self.setWorker(worker)   # get this from MUPEN core

        # set up the blanks
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
        self.save_name = ""

        # startup
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)

    def set_save_dir(self):
        """Set the input field text."""
        name = self.getGame()
        name_path = os.path.join(self.work_dir, "training", name)
        if not os.path.isdir(name_path):
            log.debug("path does not exist, creating it now: {}".format(name_path))
            os.makedirs(name_path)
        self.print_console("Good Choice with {}, Good luck!".format(name))

        self.build_selector(name_path)

        folder_len = len(os.listdir(name_path))
        path = "newGame_{}".format(folder_len)
        msg = "Ready to Save in Directory:"
        self.print_console("{}\n{}".format(
            msg, os.path.join(name_path, path)
            ))
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
            rver = 132352
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

        if not os.path.isdir(self.save_name):
            os.makedirs(self.save_name)

        self.worker.toggle_autoshots()
        self.recording = True
        self.recordStartedAt = time.time()*1000.0

    def stop(self):
        """End the recording session.

        Also buttons up the screenshot dir.
        """
        if self.recording:
            self.status("Done recording.")
            # self.poll_time.stop()
            self.worker.toggle_autoshots()
            self.actionButton.setText('Record')

            elapsed = time.time()*1000.0 - self.recordStartedAt
            self.print_console("Recording took {} seconds".format(elapsed/1000.0))
            self.recordStartedAt = None

            self.set_save_dir()
            self.recording = False
            self.get_controllers()
            self.get_images()

    def get_controllers(self):
        """Move all the controller input logs.

        To the current save_dir.
        """
        log.debug()
        input_dir = os.path.join(self.work_dir, "input/")
        log.debug("about to list dir: {}".format(input_dir))
        x = os.listdir(input_dir)
        log.debug("got stuff: {}".format(x))
        if len(x) > 0:
            y = []
            for i in x:
                y.append(i)
                # log.debug(input_dir+i)
                mv_from = os.path.join(input_dir, i)
                mv_to = self.save_name
                log.debug("moving: {} -> {}".format(
                    mv_from, mv_to
                    ))
                shutil.move(mv_from, mv_to)

            self.print_console(
                "Got {} input logs, moved to {}".format(
                    len(y), self.save_name
                    ))

        else:
            self.checkButton.setEnabled(True)
            self.print_console("No Inputs Saved")

    def get_images(self):
        """Move all the screenshots to the current save_dir."""
        log.debug()
        shot_dir = os.path.join(self.work_dir,
                                "screenshot/")
        log.debug("about to list dir: {}".format(shot_dir))
        x = os.listdir(shot_dir)
        log.debug("got stuff: {}".format(x))
        if len(x) > 0:
            y = []
            for i in x:
                y.append(i)
                # log.debug(shot_dir+i)
                mv_from = os.path.join(shot_dir, i)
                mv_to = self.save_name
                log.debug("moving: {} -> {}".format(
                    mv_from, mv_to
                    ))
                shutil.move(mv_from, mv_to)

            self.print_console(
                "Got {} images, moved to {}".format(
                    len(y),
                    self.save_name
                    ))
        else:
            self.checkButton.setEnabled(True)
            self.print_console("No ScreenShots Saved")

    def show(self):
        """Default show command."""
        # self.startupTimer()
        pass

    def hide(self):
        """Stop recording on game close."""
        # self.shutdownTimer()
        self.stop()
        super().hide()

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

    @pyqtSlot()
    def closeEvent(self, event=False): pass
