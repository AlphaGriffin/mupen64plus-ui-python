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
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from m64py.frontend.agblank import AGBlank
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QAbstractItemView
# from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import http.server
import socketserver
import sys
import numpy as np
from PIL import Image
import tensorflow as tf
from m64py.tf.mupen import mupenDataset
import ag.logging as log
VERSION = sys.version

INTRO =\
""" This is the AI Player
""".format(VERSION,)


class Player(AGBlank):
    """AG_Trainer Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker, settings):
        super().__init__(parent)
        self.setWindowTitle('AG Player')
        self.selectorLabel.setText('Existing Model Saves:')
        self.selector.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.parent = parent
        self.inputLabel.setText('Working Directory(s):')
        self.actionButton.setText('Process')
        self.actionButton.setEnabled(False)
        self.actionButton.setText('Play')
        self.checkButton.setEnabled(True)
        self.checkButton.setText('Load Model')
        self.input.setEnabled(False)
        self.selector.setEnabled(False)

        # load other classes
        self.server_thread = ServerThread(parent=self.parent)
        self.web_handler = Handler

        # booleans
        self.model_loaded = False
        self.serving = False
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
        self.selected = None
        self.selection = []
        self.selectedRom = ""
        self.gamePath = ""
        self.selectingRom = True
        
        # Use the flows
        self.sess = False
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.root_dir = self.work_dir
        self.work_dir = os.path.join(self.work_dir, "model")
        self.getSaves()

    def load_model(self):
        folder = self.gamePath
        # start a new session if you are going to switch between models
        Model_Name = "Alpha"
        Meta_Name = Model_Name + ".meta"
        self.print_console("Loading Model: {}".format(Model_Name))
        if self.sess:
            self.sess.close()

        try:
            self.sess = tf.InteractiveSession()
            metafile = os.path.join(folder, self.select_string, "Alpha.meta")
            print("trying: {}".format(metafile))
            new_saver = tf.train.import_meta_graph(metafile)
            modelfile = os.path.join(folder, self.select_string, "Alpha")
            log.debug("loading modelfile {}".format(modelfile))
            new_saver.restore(self.sess, modelfile)

            self.x = tf.get_collection_ref('input')[0]
            self.k = tf.get_collection_ref('keep_prob')[0]
            self.y = tf.get_collection_ref('final_layer')[0]
            debug = "input: {}\nkeep_prob: {}\nfinal layer: {}".format(self.x, self.k, self.y)
            log.debug(debug)
            self.print_console(debug)
            log.info("model successfully Loaded: {}/Alpha.meta".format(folder))
            self.model_loaded = True
        except Exception as e:
            self.print_console("This folder failed to produce a model. {}\nError: {}".format(folder, e))
        pass

    """ TEST FUNCTIONS """
    def start_server(self):
        log.debug("start_server()")
        socketserver.TCPServer(('', 8321), self.web_handler)

        log.debug("starting server thread")
        try:
            if self.server_thread.set_server(server):
                self.server_thread.start()
            else:
                try:
                    # try again... after a moment
                    self.server_thread.start()
                except:
                    print("server not starting")
        except Exception as e:
            log.fatal("Server not starting: {}".format(e))
            print("sucking...")

        self.print_console('Started httpserver on port 8321')

    def stop_server(self):
        log.debug("stop_server")
        self.server_thread.stop()
        return True

    """ Selector FUNCTIONS """
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
        self.actionButton.setEnabled(False)
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
        self.selection = selection
        self.select_string = select_string
        
        # if we have picked a game
        if any(select_string in s for s in self.gamesList):
            self.currentGame = self.selected[0].text()
            self.selectingRom = False
            x = os.path.join(self.work_dir,self.currentGame)
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
        
    def setWorker(self, worker):
        """Get Worker from main code and check the local Userdata folder"""
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        # self.work_dir = os.path.join(self.work_dir, "training")
           
    def build_selector(self, folder=""):
        """This populates the save folder list"""
        self.selector.clear()
        if not self.selectingRom or folder is not "": 
            self.selector.addItem("../")
            for i in sorted(os.listdir(folder)):
                self.selector.addItem("{}".format(i))   
        else:
            for i in self.gamesList:
                self.selector.addItem("{}".format(i))
        """then we need to be selecting folders to process"""
                    
    def show(self):
        """On Show this window"""
        super().show()
        
    def hide(self):
        """On hide this window"""
        super().hide()
    
    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Process the files"""
        self.processing_()
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        # reset and select game again...
        if not self.model_loaded:
            self.load_model()
            self.checkButton.setText('Start Server')

        else:
            if self.serving:
                self.stop_server()
                self.checkButton.setText('Start Sever')
                self.serving = False

            else:
                self.start_server()
                self.checkButton.setText('Stop Server')
                self.serving = True

    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        self.selected = self.selector.selectedItems()
        if len(self.selected) > 0:
            self.selecterator()
            return
        self.actionButton.setEnabled(False)
        
    @pyqtSlot()
    def closeEvent(self,event=False): pass


class ServerThread(QThread):
    """Thread for running the web server"""

    def set_server(self, server__):
        self.server = server__
        self.server_running = 1
        log.debug("Server set in thread")
        return True

    def run(self):
        """Call to action the server_forever method"""
        log.debug("ServerThread run()")
        while self.server_running:
            self.server.handle_request()
            log.info("ServerThread is running")

    def stop(self):
        log.debug("ServerThread run()")
        self.server_running = 0
        # this is not working :(

class Handler(http.server.SimpleHTTPRequestHandler):
    def output(self, data):
        log.debug("   set response_message <- {}".format(data))
        output = [
                int(data[0] * 80),
                int(data[1] * 80),
                int(round(data[2])),
                int(round(data[3])),
                int(round(data[4])),
            ]
        self.response_message = output

    def do_GET(self):
        # Construct a server response.
        message = ""
        try:
            message = self.response_message
        except:
            message = "Hello Prof. Falken,\n\n\tWorld you like to play a game?"
            pass
        self.send_response(20)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))
        return


class TensorPlay(object):
    """Actual connection to TensorFlow subsystem and image processing"""

    def __init__(self, autoshots_path):
        log.debug("TensorPlay init: {}".format(autoshots_path))

        self.sess = None
        self.autoshots = autoshots_path

    def load_graph(self, folder):
        """Load the trained model from the given folder path"""
        log.debug("load_graph(): folder = {}".format(folder))
        log.info("starting TensorFlow version {} session...".format(tf.__version__))
        self.sess = tf.InteractiveSession()
        model_file = os.path.join(folder, "Alpha.meta")
        new_saver = tf.train.import_meta_graph(model_file )
        log.debug("Training this model: {}".format(model_file))
        new_saver.restore(sess, os.path.join(folder, "Alpha"))

        self.x = tf.get_collection_ref('input')[0]
        self.k = tf.get_collection_ref('keep_prob')[0]
        self.y = tf.get_collection_ref('final_layer')[0]
        log.info("model successfully Loaded: {}/Alpha.meta".format(folder))
        # img = prepare_image(img)
        # feed_dict = {x: [img], k: 1.0}
        # classification = sess.run(y, feed_dict)
        # return classification

    def dequeue_image(self, remove=True):
        """Find next autoshot image, load and return it while removing it from disk"""

        # FIXME: we have a contention problem reading an image file from disk so quickly
        #       and adding sync() calls in mupen64plus-core causes some bad stuttering,
        #       so we'll need to work out a better way to pass the images through

        images = os.listdir(self.autoshots)
        if not images:
            return None

        file = images[0]
        log.debug("found file: {}".format(file))
        time.sleep(.005)  # 5 ms enough? FIXME

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
            log.debug("pil_image resized: {}".format(x))
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
        try:
            feed_dict = {self.x: [vec], self.k: 1.0}
            joystick = self.sess.run(self.y, feed_dict)
            log.debug("{}".format(joystick))
            output = [
                int(joystick[0] * 80),
                int(joystick[1] * 80),
                int(round(joystick[2])),
                int(round(joystick[3])),
                int(round(joystick[4])),
            ]
            log.debug("   classification: {}".format(output))
            return output

        except Exception as e:
            log.fatal("Exception evaluating model: {}".format(e))

    def forget(self):
        """Wrap it up (close session, clean up)"""
        log.debug("closing TensorFlow session...")
        self.session.close()
        log.info("TensorFlow session closed")