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
from PyQt5.QtCore import pyqtSlot, QThread  # , QTimer
from PyQt5.QtWidgets import QAbstractItemView
from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys, time  # , shutil
# from glob import glob as check
import numpy as np
import tensorflow as tf
from PIL import Image
from PIL import ImageFile
import traceback

ImageFile.LOAD_TRUNCATED_IMAGES = True  # FIXME?

import ag.logging as log
import tensorflow as tf
# import m64py.tf.model as Model

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

class Player(AGBlank):
    """AG_Player Widget of MuPen64 Python Ui"""

    #
    # STEP 0 - default setup
    #

    def __init__(self, parent, worker, settings):
        """ @param parent   QDialog (mainwindow)
            @param worker   Mupen worker object
            @param settings Settings dialog instance from mainwindow """
        # basic set-up
        super().__init__(parent)
        self.setWorker(worker, 'model')
        self.setWindowTitle('AG Player')
        self.settings = settings
        self.print_console("AlphaGriffin.com - AI Player")

        # AI machine player
        self.ai_player = TensorPlay(os.path.join(self.root_dir, 'screenshot'))
        self.ai_thread = PlayerThread(self, self.ai_player)
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

        # check2 button starts server
        self.check2Button.setText('Thing 2')
        self.check2Button.setEnabled(False)

        # status flags
        self.playing = False
        self.serving = False
        self.selected = None
        self.model_loaded = False
        self.playing_game = False
        self.selection = []
        self.selectedRom = ""
        self.gamePath = ""
        self.selectingRom = True
        self.sess = False
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.root_dir = self.work_dir
        self.work_dir = os.path.join(self.work_dir, "model")

        # all set!
        self.print_console(INTRO)
        self.getSaves()


    # INPUT FUNCTIONS
    def prepareInputPlugin(self, load):  # FIXME NOT DONE
        """Pause ROM state, swap input plugin (load or unload), resume ROM"""
        if load:
            self.print_console("Switching to the mupen64plus-input-bot module")
        else:
            self.print_console("Switching back to user input module")

        plugins = self.settings.qset.value("Path/Plugins", os.path.realpath(
            os.path.dirname(self.worker.plugin_files[0])))
        log.debug("prepareInputPlugin(): {}".format(plugins))

        # see also settings.py set_plugins()

        # all this really necessary?
        # self.parent.worker.plugins_shutdown()
        # self.parent.worker.plugins_unload()
        ###self.parent.worker.plugins_load(path)
        # self.parent.worker.plugins_startup()

        log.warn("prepareInputPlugin(): NOT DONE")

    def start_server(self):
        return self.ai_thread.start_server()

    def stop_server(self):
        return self.ai_thread.stop_server()

    def start_playing(self):
        log.info("Waking up the AI to play...")

        self.start_server()
        folder = os.path.join(self.gamePath, self.select_string)
        self.ai_thread.load_n_check(folder)

        # FIXME: this is a hack to get us through the mario kart menus...
        for i in range(100):
            self.ai_thread.web_handler.output([0, 0, 1, 0, 0])

        #self.ai_thread.start()

        #self.playing_game = True

    def stop_playing(self):
        log.info("The AI is going to sleep...")

        self.stop_server()

        self.playing_game = False

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
        log.debug("on_checkButton_clicked(): Check Test")
        folder = os.path.join(self.gamePath, self.select_string)
        self.ai_thread.load_n_check(folder)
        log.debug("load_graph FINISHED!")

        #log.debug("starting server")


        """
        if not self.model_loaded:
            # self.load_model()
            folder = os.path.join(self.gamePath, self.select_string)

            if self.ai_player.load_graph(folder):
                self.checkButton.setText('Start Server')
                self.actionButton.setEnabled(True)
                self.model_loaded = True

        else:
            if self.serving:
                self.stop_server()
                self.checkButton.setText('Start Sever')
                self.serving = False

            else:
                self.start_server()
                self.checkButton.setText('Stop Server')
                self.serving = True
        """

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Process the files"""
        try:
            """
            if  self.model_loaded is True:
                test = self.tf_service()
                if not test:
                    self.print_console("Cannot Proceed, Check your files!")
                    return False
                self.print_console("Model Test Result: {}".format(test))
                self.actionButton.setText('Start Game')
            else:
            """

            if not self.playing_game:
                self.print_console("Starting AI Player... Good Luck!")
                self.start_playing()
                self.actionButton.setText('Stop Game')
            else:
                self.print_console("Stopping AI Player... Good Job!")
                self.stop_playing()
                self.actionButton.setText('Start Game')
            #else:
            #    self.print_console("You need to Test your Model")
            #    self.actionButton.setText('Test Check')
        except Exception as e:
            log.fatal()
            raise e

    # ON WINDOW EVENTS
    def hide(self):
        """Hide this window"""

        if self.playing:
            self.ai_thread.playing = False  # this signals the thread to quit on its own, cleanly
            self.print_console("Waiting for AI to settle down")
            self.debug("waiting for ai_thread to finish...")
            self.ai_thread.wait()
            self.playing = False;
            self.actionButton.setText("Play")

        super().hide()

    def show(self):
        """Show this window"""
        super().show()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#
# CORE FUNCTIONALITY
#


class PlayerThread(QThread):
    """Thread for the TensorPlay image classifier (which is the real brains)"""

    def __init__(self, parent, thinker):
        log.debug("PlayerThread init: {}".format(thinker))
        super().__init__(parent)

        self.parent = parent
        self.thinker = thinker
        self.model_path = None
        self.web_handler = PlayerInputRequestHandler()
        self.server_thread = ServerThread(parent=self.parent)
        self.loaded_graph = False
        self.playing = True

    def load_n_check(self, model_path):
        if self.thinker.load_graph(model_path):
            self.loaded_graph = True
            return True
        else:
            return False


    def run(self):
        log.info("PlayerThread running");

        # on your marks...
        # self.model_path = self.parent.input.text()
        # self.thinker.load_graph(self.model_path)

        # get ready...
        # self.parent.print_console("Starting local HTTP server for AI input pass-through")
        # self.start_server()
        # FIXME: remove any files from screenshot folder automatically before we start?
        self.parent.print_console("Turning on autoshots")
        self.parent.worker.toggle_autoshots()

        # set...
        self.parent.print_console("All set!")
        self.parent.actionButton.setEnabled(True)

        # go!
        while self.playing:
            image = self.thinker.dequeue_image()
            if image is not None and image is not False:
                try:
                    moves = self.thinker.classify_image(image)
                    self.web_handler.output(moves)
                    self.parent.print_console(" -> {}".format(moves))
                    log.debug("here again")
                except Exception as e:
                    log.fatal("Exception trying to play", e)

            else:
                time.sleep(.01)  # waiting 10 ms

        # peace out
        log.debug("player thread cleaning up...")
        self.parent.worker.toggle_autoshots()
        self.stop_server()
        self.thinker.forget()

        log.info("PlayerThread done")

    def start_server(self):
        log.debug("start_server()")
        server = HTTPServer(('', 8321), self.web_handler)

        log.debug("starting server thread")
        self.server_thread.set_server(server)
        self.server_thread.start()

        self.parent.print_console('Started httpserver on port 8321')

    def stop_server(self):
        log.debug("stop_server()")
        self.server_thread.quit()
        return True


class TensorPlay(object):
    """Actual connection to TensorFlow subsystem and image processing"""

    def __init__(self, autoshots_path):
        log.debug("TensorPlay init: {}".format(autoshots_path))

        self.session = None
        self.autoshots = autoshots_path

    def load_graph(self, folder, game=None):
        """Load the trained model from the given folder path"""
        log.debug("load_graph(): folder = {}".format(folder))
        try:
            self.session = tf.InteractiveSession()
            # new_path = "/Users/lannocc/.local/share/mupen64plus/model/outputmodel12/mupen64_mariokart64"
            new_path = os.path.join(folder, "Mupen64plus")
            meta_path = new_path + ".meta"
            new_saver = tf.train.import_meta_graph(meta_path)
            self.session.run(tf.global_variables_initializer())
            new_saver.restore(self.session, new_path)
        except Exception as e:
            log.fatal(traceback.format_exc())

        # FIXME: we have a situation here: there was no summary attached to this graph... gotta redo it.. :(
        self.x = tf.get_collection_ref('x_image')[0]
        self.k = tf.get_collection_ref('keep_prob')[0]
        self.y = tf.get_collection_ref('y')[0]
        debug = "input: {}\nkeep_prob: {}\nfinal layer: {}".format(self.x, self.k, self.y)
        log.debug("input", x=self.x, k=self.k, y=self.y)
        log.info("model successfully loaded")
        return True

    def dequeue_image(self, remove=False):
        """Find next autoshot image, load and return it while removing it from disk"""

        # FIXME: we have a contention problem reading an image file from disk so quickly
        #       and adding sync() calls in mupen64plus-core causes some bad stuttering,
        #       so we'll need to work out a better way to pass the images through
        #   see HACK below

        images = os.listdir(self.autoshots)
        if not images:
            return None

        # HACK: wait for 2 images before we do anything (thanks to ruckusist for the idea)
        if len(images) < 2:
            return None

        file = images[0]
        log.debug("found file: {}".format(file))
        #time.sleep(.005)  # 5 ms enough? FIXME

        # load image into memory (performing minor processing) and remove from disk
        img = self.prepare_image(os.path.join(self.autoshots, file))

        if remove:
            log.debug("removing image")
            try:
                os.remove(os.path.join(self.autoshots, file))
            except Exception as e:
                log.fatal("Exception removing image: {}".format(e))

        return img

    def prepare_image(self, img, makeBW=False):
        """ This resizes the image to a tensorflowish size """
        log.debug("prepare_image: {}".format(img))
        try:
            pil_image = Image.open(img)  # open img
            log.debug("pil_image: {}".format(pil_image))
            x = pil_image.resize((200, 66), Image.ANTIALIAS)  # resizes image
        except Exception as e:
            log.fatal("Exception: {}".format(e))
            return False

        # log.debug("   x: {}".format(x))
        numpy_img = np.array(x)  # convert to numpy
        # log.debug("   numpy_img: {}".format(numpy_img))
        # if makeBW:
        #    numpy_img = self.make_BW(numpy_img)           # grayscale
        return numpy_img

    def classify_image(self, vec):
        """Return labels matching the supplied image. Image should already be prepared."""
        log.debug("classify_image()")
        #log.debug("vec", shape=vec.shape[:])

        try:
            feed_dict = {self.x: [vec], self.k: 1.0}
            #log.debug("about to run session", feed_dict=feed_dict)
            joystick = self.session.run(self.y, feed_dict)
            log.debug("{}".format(joystick))
            joystick = joystick[0] # because an array of array is originally returned
            output = [
                int(joystick[0] * 80),
                int(joystick[1] * 80),
                int(0), # START BUTTON
                int(round(joystick[2])),
                int(round(joystick[3])),
                int(round(joystick[4])),
            ]

            log.debug("   classification: {}".format(output))
            return output
        except Exception as e:
            log.fatal("Exception evaluating model: {}".format(e))
            pass

    def forget(self):
        """Wrap it up (close session, clean up)"""
        log.debug("closing TensorFlow session...")
        self.session.close()
        log.info("TensorFlow session closed")


class ServerThread(QThread):
    """Thread for running the web server"""

    def set_server(self, server):
        log.debug("set_server(): {}".format(server))
        self.server = server

    def quit(self):
        self.running = False

    def run(self):
        log.debug("ServerThread run()")
        #self.server.serve_forever()

        self.running = True
        while not self.running:
            self.server.handle_request()


class PlayerInputRequestHandler(BaseHTTPRequestHandler):
    """Request handler for httpserver that sends controller commands upon request from the input plugin"""

    def __init__(self):
        self.response_message = [0, 0, 0, 0, 0]

    def output(self, data):
        log.debug("   set response_message <- {}".format(data))
        self.response_message = data

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        ### calibration
        #        output = [
        #            int(self.response_message[0] * 80),
        #            int(self.response_message[1] * 80),
        #            int(round(self.response_message[2])),
        #            int(round(self.response_message[3])),
        #            int(round(self.response_message[4])),
        #        ]

        log.debug("    <<< GET >>> :AI: {}".format(str(output)))

        ### respond with action
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(self.response_message)  # this is the output to http here

        return True
