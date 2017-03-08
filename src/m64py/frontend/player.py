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
import os, sys, time #, shutil
#from glob import glob as check
import numpy as np
import tensorflow as tf
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True  # FIXME?

import ag.logging as log
import m64py.tf.model as Model
import m64py.tf.build_network as Network
from m64py.tf.mupen import mupenDataset as Data

VERSION = sys.version

# FIXME
INTRO =\
"""
ARTIFICIAL PLAYER:
        FIXME
""".format(VERSION,)

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
        self.ai_thread = PlayerThread(self, TensorPlay(os.path.join(self.root_dir, 'screenshot')))
        # AI will communicate with game through a WEBSERVER

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
            self.print_console("You Selected: {}".format(self.selected))
            self.print_console("")
            self.print_console("    Hit  << Play >>  when ready")
            self.print_console("")
            self.print_console(" (don't forget to load a ROM first and get to position)")

    #
    # STEP 2 - start playing!
    #

    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        log.warn("on_checkButton_clicked(): NOT IMPLEMENTED")  # FIXME?

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Check game running state and if so start the play process"""
        if self.playing:
            self.ai_thread.playing = False  # this signals the thread to quit on its own, cleanly
            self.prepareInputPlugin(False)
            self.print_console("Waiting for AI to settle down")
            log.debug("waiting for ai_thread to finish...")
            self.actionButton.setEnabled(False)
            try:
                self.ai_thread.wait()
                log.debug("thread out")
                self.playing = False
                self.actionButton.setText("Play")
                self.actionButton.setEnabled(True)
            except Exception as e:
                log.fatal("Exception stopping: {}".format(e))

        else:
            self.worker.core_state_query(1)
            log.debug("worker state: {}".format(self.worker.state))
            loaded = self.worker.state in [2, 3]

            if loaded:
                log.info("getting ready to play...")
                self.prepareInputPlugin(True)
                self.ai_thread.start()
                self.print_console("AI player thread started")

                self.print_console("It may take a moment for TensorFlow startup...")
                self.actionButton.setText('Stop')
                self.actionButton.setEnabled(False)
                self.playing = True

            else:
                self.print_console('SORRY...')
                self.print_console('    You must load a ROM first for me to play')
 
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
        #self.parent.worker.plugins_shutdown()
        #self.parent.worker.plugins_unload()
        ###self.parent.worker.plugins_load(path)
        #self.parent.worker.plugins_startup()

        log.warn("prepareInputPlugin(): NOT DONE")

    #
    # STEP 3 - giving up already?
    #

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

        self.playing = True

    def run(self):
        log.info("PlayerThread running");
 
        # on your marks...
        self.model_path = self.parent.input.text()
        self.thinker.load_graph(self.model_path)

        # get ready...
        self.parent.print_console("Starting local HTTP server for AI input pass-through")
        self.start_server()
        self.parent.print_console("Turning on autoshots")
        self.parent.worker.toggle_autoshots()

        # set...
        self.parent.print_console("All set!")
        self.parent.actionButton.setEnabled(True)

        # go!
        while self.playing:
            image = self.thinker.dequeue_image()
            if image is not None:
                moves = self.thinker.classify_image(image)
                self.thinker.web_handler.output(moves)
                self.print_console(" -> {}".format(moves))

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

    def load_graph(self, folder):
        """Load the trained model from the given folder path"""
        log.debug("load_graph(): folder = {}".format(folder))

        log.info("starting TensorFlow version {} session...".format(tf.__version__))
        self.session = tf.InteractiveSession()
        #graphfile = os.path.join(folder, 'graph.pbtxt')
        #log.debug("Graphfile:\n\t{}".format(graphfile))
        #self.graph = tf.import_graph_def(graphfile,
        #                            # return_elements=['data/inputs:0',
        #                            #                  'output/network_activation:0',
        #                            #                  'data/correct_outputs:0'],
        #                               name='')
        #log.debug("{}".format(self.graph))
        metafile = os.path.join(folder, 'alpha.griffin-0.meta')
        log.debug("   metafile: {}".format(metafile))

        log.debug("   tf.train.import_meta_graph()...")
        saver = tf.train.import_meta_graph(metafile)

        log.debug("   saver.restore()...")
        saver.restore(sess=self.session, save_path=metafile)

        log.info("model successfully loaded")

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
        time.sleep(.005) # 5 ms enough? FIXME

        
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
            pil_image = Image.open(img)                       # open img
            log.debug("pil_image: {}".format(pil_image))
            x = pil_image.resize((200, 66), Image.ANTIALIAS)  # resizes image
            log.debug("pil_image resized: {}".format(x))
        except Exception as e:
            log.fatal("Exception: {}".format(e))
            return False

        #log.debug("   x: {}".format(x))
        numpy_img = np.array(x)                           # convert to numpy
        #log.debug("   numpy_img: {}".format(numpy_img))
        # if makeBW:
        #    numpy_img = self.make_BW(numpy_img)           # grayscale
        return numpy_img

    def classify_image(self, vec):
        """Return labels matching the supplied image. Image should already be prepared."""

        #joystick = _best_validation_1_
        try:
            model = Network.Build_Adv_Network(Data(init=False))
            #with self.graph as tf.Graph:
            joystick = model.x_image.eval(session=self.session, feed_dict={model.Input_Tensor_Images: [vec], model.keep_prob: 1.0}) # [0]
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



class ServerThread(QThread):
    """Thread for running the web server"""

    def set_server(self, server):
        log.debug("set_server(): {}".format(server))
        self.server = server

    def run(self):
        log.debug("ServerThread run()")
        self.server.serve_forever()


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

