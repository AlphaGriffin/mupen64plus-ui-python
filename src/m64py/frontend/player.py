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


class webServer(BaseHTTPRequestHandler):
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

class AThread(QThread):

    def set_server(self, server):
        self.server = server

    def run(self):
        self.server.serve_forver()


class Play(object):

    def __init__(self):
        #self.options = options
        # need some pathy kind of stuff here
        #self.save_path = self.options.save_dir + '_best_validation_1_'
        x=0

    def load_graph(self, session):
        session = tf.Session
        saver = tf.train.Saver()

        # this path here will be passed by the selectorator
        # THERE ARE NO FILE EXTIONONS IN THE FUTURE!!!!
        save_path = self.options.log_dir + 'alpha.griffin'
        saver.restore(sess=session, save_path=save_path)

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


class Player(AGBlank):
    """AG_Player Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        super().__init__(parent)
        self.setWindowTitle('AG Player')
        self.print_console("AlphaGriffin.com - AI Player")
        # AI machine player
        self.ai_player = Play()  # SHIT... where are the options?
        # AI will communicate with game through a WEBSERVER
        self.server_thread = AThread(parent=self)
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
        self.serving = False
        self.selected = None
 
        # all set!
        self.print_console(INTRO)
    



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

           
    def play_game(self, folder):
        # if game is on and going
        # Start autoshots
        # start get screenshots
        # load the model and keep it open
        ## Think
        joystick = model.y.eval(feed_dict={model.x: [vec], model.keep_prob: 1.0})[0]
        # Post the label to the webserver
        # webserver.response_message = joystick
        pass

    def start_server(self):
        self.web_server = webServer()
        server = HTTPServer(('', 8321), self.web_server)
        self.server_thread = AThread(parent=self)
        self.server_thread.set_server(server)
        self.server_thread.start()
        self.print_console('Started httpserver on port 8321')

    def stop_server(self):
        self.server_thread.quit()
        return True

    def get_screenshots(self):
        # search screenshot dir and start a que
        # go as fast as you can...
        # pring to log how far behind youre getting

        pass

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Process the files"""
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        # reset and select game again...
        self.start_server()
        self.print_console("Starting Server")
         
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

    def show(self):
        """Show this window"""
        super().show()

        if not self.selector.isEnabled():
            self.populateSelector()
            self.selector.setEnabled(True)

    def hide(self):
        """Hide this window"""
        super().hide()
