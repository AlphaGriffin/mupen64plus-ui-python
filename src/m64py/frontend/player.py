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
from PyQt5.QtCore import pyqtSlot, QThread#, QTimer
from PyQt5.QtWidgets import QAbstractItemView
from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys#, time, shutil
#from glob import glob as check
import numpy as np
import tensorflow as tf
from PIL import Image

import ag.logging as log

VERSION = sys.version

# FIXME
INTRO =\
"""
ARTIFICIAL PLAYER:
        FIXME
""".format(VERSION,)


class Player(AGBlank):
    """AG_Player Widget of MuPen64 Python Ui"""

    #
    # STEP 0 - default setup
    #

    def __init__(self, parent, worker):
        # basic set-up
        super().__init__(parent)
        self.setWorker(worker, 'model')
        self.setWindowTitle('AG Player')
        self.print_console("AlphaGriffin.com - AI Player")

        # AI machine player
        self.ai_player = TensorPlay()
        # AI will communicate with game through a WEBSERVER
        self.server_thread = ServerThread(parent=self)

        # model selector (don't populate it until window is actually shown)
        self.selectorLabel.setText('Existing Trained Models:')
        self.selector.setEnabled(False)

        # using input as full selected path readout (read-only for now)
        self.inputLabel.setText('full selected path:')
        self.input.setEnabled(False)
 
        # play button
        self.actionButton.setText('Play')
        self.actionButton.setEnabled(False)

        # not using checkButton (yet)
        self.checkButton.setEnabled(False)
       
        # status flags
        self.playing = False
        self.serving = False
        self.selected = None
 
        # all set!
        self.print_console(INTRO)

    #
    # STEP 1 - open window and pick a previously-trained model
    #
       
    def show(self):
        """Show this window"""
        super().show()

        if not self.selector.isEnabled():
            self.populateSelector()
            self.selector.setEnabled(True)
    
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
         
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        log.debug("on_selector_itemSelectionChanged()")
        self.selected = None;

        selected = self.selector.selectedItems()
        if len(selected) is 1:
            log.debug("got a selection")
            self.selected = selected[0].text();
            self.input.setText(os.path.join(self.work_dir, self.selected))
            self.actionButton.setEnabled(True)

    #
    # STEP 2 - let's go!
    #

    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        log.warn("on_checkButton_clicked(): NOT IMPLEMENTED")  # FIXME?

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Check game running state and if so start the play process"""
        self.worker.core_state_query(1)
        loaded = self.worker.state in [2, 3]

        if loaded:
            log.info("getting ready to play...")
            play_game()

        else:
            self.print_console('SORRY...')
            self.print_console('    You must load a ROM first for me to play')
            
    def play_game(self):
        """(ROM should already be running) Delegate to TensorPlay to load model, start auto-shots & webserver"""

        self.ai_player.load_graph(self.input.text())

        # if game is on and going
        # Start autoshots
        # start get screenshots
        # load the model and keep it open
        ## Think
        joystick = model.y.eval(feed_dict={model.x: [vec], model.keep_prob: 1.0})[0]
        # Post the label to the webserver
        # webserver.response_message = joystick
        pass

    def get_screenshots(self):
        # search screenshot dir and start a que
        # go as fast as you can...
        # pring to log how far behind youre getting

        pass

    #
    #
    #

    def start_server(self):
        self.web_server = webServer()
        server = HTTPServer(('', 8321), self.web_server)
        self.server_thread.set_server(server)
        self.server_thread.start()
        self.print_console('Started httpserver on port 8321')

    def stop_server(self):
        self.server_thread.quit()
        return True

    def hide(self):
        """Hide this window"""
        super().hide()



class TensorPlay(object):
    """Actual connection to TensorFlow subsystem and image processing"""

    def __init__(self):
        #self.options = options
        # need some pathy kind of stuff here
        #self.save_path = self.options.save_dir + '_best_validation_1_'
        x=0

    def load_graph(self, folder):
        """Load the trained model from the given folder path"""
        log.debug("load_graph(): folder = {}".format(folder))

        log.info("starting TensorFlow session...")
        session = tf.Session
        saver = tf.train.Saver()

        # this path here will be passed by the selectorator
        # THERE ARE NO FILE EXTIONONS IN THE FUTURE!!!!
        save_path = folder + 'alpha.griffin'
        log.debug("restoring: {}".format(save_path))
        saver.restore(sess=session, save_path=save_path)
        log.info("model successfully loaded")

    def classify(self, Image):
        img = prepare_image(Image)
        joystick = _best_validation_1_
        output = [
            int(joystick[0] * 80),
            int(joystick[1] * 80),
            int(round(joystick[2])),
            int(round(joystick[3])),
            int(round(joystick[4])),
        ]

    def prepare_image(self, img, makeBW=False):
        """ This resizes the image to a tensorflowish size """
        pil_image = Image.open(img)                       # open img
        x = pil_image.resize((200, 66), Image.ANTIALIAS)  # resizes image
        numpy_img = np.array(x)                           # convert to numpy
        # if makeBW:
        #    numpy_img = self.make_BW(numpy_img)           # grayscale
        return numpy_img



class PlayerInputServer(BaseHTTPRequestHandler):
    """A simple web server that, upon request from the input plugin, sends controller commands"""
    def __init__(self):
        self.response_message = []

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        ### calibration
        output = [
            int(self.response_message[0] * 80),
            int(self.response_message[1] * 80),
            int(round(self.response_message[2])),
            int(round(self.response_message[3])),
            int(round(self.response_message[4])),
        ]

        message = "Got Get request.\n\tAI: {}".format(str(output))

        ### respond with action
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(output)  # this is the output to http here
        return message


class ServerThread(QThread):
    """Thread for running the web server"""

    def set_server(self, server):
        self.server = server

    def run(self):
        self.server.serve_forver()

