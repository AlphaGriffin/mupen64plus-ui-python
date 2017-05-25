# -*- coding: utf-8 -*-
# Author: lannocc and ruckusist @ AlphaGriffin <Alphagriffin.com>
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

from m64py.frontend.aicommon import AICommon
from PyQt5.QtCore import pyqtSlot, QThread
import os, sys, socket, time
from m64py.utils import version_split
from m64py.core.defs import Buttons
import ag.logging as log

VERSION = sys.version

# FIXME
INTRO = \
    """
    ARTIFICIAL PLAYER:
            FIXME
    """.format(VERSION, )


#
# USER INTERFACE
#

class Player(AICommon):
    """AG_Player Widget of MuPen64 Python Ui"""

    def __init__(self, parent, status, worker, backend):

        # basic set-up
        super().__init__(parent, status)
        self.setWorker(worker, 'model')
        self.print_console("AlphaGriffin.com - AI Player")

        # backend and thread
        self.backend = backend
        self.backend.autoshots = os.path.join(self.root_dir, 'screenshot')
        self.thread = PlayerThread(self, backend, worker)

        # AI machine player
        #self.ai_player = TensorPlay(os.path.join(self.root_dir, 'screenshot'))
        #self.ai_thread = PlayerThread(self, self.ai_player)
        # AI will communicate with game through a WEBSERVER

        # model selector (don't populate it until window is actually shown)
        self.selectorLabel.setText('Existing Trained Models:')
        self.selector.setEnabled(True)

        # using input as full selected path readout (read-only for now)
        self.inputLabel.setText('full selected path:')
        self.input.setEnabled(False)

        # play button
        self.actionButton.setText('Play')
        self.actionButton.setEnabled(False)

        # check button starts server
        self.checkButton.setText('Thing 1')
        self.checkButton.setEnabled(False)

        # check2 button is not used
        self.check2Button.hide()

        # status flags
        self.playing = False
        self.serving = False
        self.selected = None
        self.model_loaded = False
        self.selection = []
        self.selectedRom = ""
        self.gamePath = ""
        self.selectingRom = True

        # all set!
        self.print_console(INTRO)
        self.getSaves()


    # SELECTOR FUNCTIONS
    def populateSelector(self):
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
        self.checkButton.setEnabled(True)
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
        self.print_console("Selected: {}".format(select_string))
        log.debug(select_string)
        self.selection = selection
        self.select_string = select_string

        # if we havent picked a game
        if any(select_string in s for s in self.gamesList):
            self.currentGame = self.selected[0].text()
            self.selectingRom = False
            x = os.path.join(self.work_dir, self.currentGame)
            if os.path.isdir(x):
                self.print_console("Game Save Dir: {}".format(x))
                self.gamePath = x
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
        # if we have a model here... just load it...
        # current_path = os.path.join(self.gamePath, self.select_string)


    def build_selector(self, folder=""):
        """This populates the save folder list"""
        self.selector.clear()
        if not self.selectingRom or folder is not "":
            self.selector.addItem("../")
            for i in sorted(os.listdir(folder)):
                if '.' in i[-1]:
                    pass
                else:
                    self.selector.addItem("{}".format(i))
        else:
            for i in self.gamesList:
                self.selector.addItem("{}".format(i))
        """then we need to be selecting folders to process"""

    # SELECTOR CLICK
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        log.debug("on_selector_itemSelectionChanged()")
        self.selected = self.selector.selectedItems()
        if len(self.selected) > 0:
            self.selecterator()
            return
        self.actionButton.setEnabled(False)
        """
        self.selected = None;

        # selected = self.selector.selectedItems()
        selected = "/home/eric/.local/share/mupen64plus/model"
        if len(selected) is 1:
            log.debug("got a selection")
            self.selected = selected[0].text();
            # self.input.setText(os.path.join(self.work_dir, self.selected))
            self.input.setText(os.path.join(self.work_dir, self.selected))
            self.actionButton.setEnabled(True)
            self.print_console("You Selected: {}".format(self.selected))
            self.print_console("")
            self.print_console("    Hit  << Play >>  when ready")
            self.print_console("")
            self.print_console(" (don't forget to load a ROM first and get to position)")
        """

    # BUTTON CLICKS
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        log.debug()

        try:
            self.status("Loading model...")  # FIXME: we don't actually see this
            folder = os.path.join(self.gamePath, self.select_string)
            self.backend.load_graph(folder)  
            self.status("Model loaded.")
            log.debug("load_graph FINISHED!")
        except Exception:
            log.error()

    @pyqtSlot()
    def on_check2Button_clicked(self):
        log.debug()
        self.worker.core_state_query(1)
        loaded = self.worker.state in [2, 3]

        if not loaded:
            self.print_console("Sorry, a ROM must be running first.")
            return

        try:
            self.worker.ai_play()

            thread = PlayerTest(self)
            thread.start()

        except Exception:
            log.error()

    @pyqtSlot()
    def on_actionButton_clicked(self):
        try:
            if not self.thread.isRunning():
                # make sure a ROM is loaded
                self.worker.core_state_query(1)
                loaded = self.worker.state in [2, 3]
                if not loaded:
                    self.print_console("Sorry, you must open a ROM first.")
                    return

                # check for required input plugin (FIXME: move this to AICommon?)
                plugins = self.worker.get_plugins()
                pinput = plugins.get(4)
                if not pinput:
                    pmap = list(self.worker.core.plugin_map[4].values())[0]
                else:
                    pmap = self.worker.core.plugin_map[4][pinput]
                log.debug("detected input plugin", map=pmap)
                pname = pmap[3]
                rname = 'Mupen64Plus SDL Input Plugin - A.G.E.'
                pver = pmap[4]
                rver = int('0x030000', 16)
                self.print_console("Input plugin detected: {} v{}".format(
                        pname, version_split(pver)))
                if not (pname == rname and pver >= rver):
                    self.print_console("SORRY...input plugin mismatch")
                    self.print_console("   required: {} >= v{}".format(
                        rname, version_split(rver)))
                    log.error("Wrong input plugin", name=pname,
                            version=version_split(pver), required_name=rname,
                            required_version=version_split(rver))
                    return

                self.print_console("Starting AI Player... Good Luck!")
                self.thread.folder = os.path.join(self.gamePath, self.select_string)
                self.thread.start()

            else:
                self.print_console("Stopping AI Player... Good Job!")
                self.actionButton.setEnabled(False)
                self.thread.done = True

        except Exception:
            log.error()



class PlayerThread(QThread):

    def __init__(self, ui, backend, worker):
        QThread.__init__(self, ui)
        self.ui = ui
        self.backend = backend
        self.worker = worker
        self.folder = None
        self.done = False

    def run(self):
        self.ui.actionButton.setText('Stop')
        sock = None

        try:
            self.worker.ai_play()

            port = 4420
            self.ui.status("Connecting to emulator port {}".format(port))
            time.sleep(1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', port))
            log.info("Connected to emulator", port=port)

            self.ui.status("Loading Model...")
            self.backend.load_graph(self.folder)

            self.ui.status("Now playing...")
            data = Buttons()

            while not self.done:
                image = self.backend.dequeue_image(True)
                if image is not None and image is not False:
                    moves = self.backend.classify_image(image)
                    self.ui.status("AI decides {}".format(moves))
                    #self.ui.print_console(moves)

                    # due to possible weak training, some moves may not be valid
                    # adjust them to fit before sending to the emulator
                    if moves[0] < -80:      moves[0] = -80
                    elif moves[0] > 80:     moves[0] = 80
                    if moves[1] < -80:      moves[1] = -80
                    elif moves[1] > 80:     moves[1] = 80
                    for i in range(2, 5):
                        if moves[i] > 1:    moves[i] = 1
                        elif moves[i] < 0:  moves[i] = 0

                    data.bits.X_AXIS = moves[0]
                    data.bits.Y_AXIS = moves[1]
                    data.bits.A_BUTTON = moves[2]
                    data.bits.B_BUTTON = moves[3]
                    data.bits.R_TRIG = moves[4]

                    count = sock.send(data)
                    if count != 4:
                        log.warn("Incomplete send of controller input", sent=count)

            self.ui.status("Done playing.")

        except Exception as e:
            log.error()
            self.ui.status("Error while playing: {}".format(e))

        try:
            if sock is not None:
                sock.close()
            self.worker.ai_stop()
        except Exception:
            log.error()

        self.backend.forget()  # shutdown session, cleanup, etc.
        self.done = False

        self.ui.actionButton.setText('Play')
        self.ui.actionButton.setEnabled(True)

