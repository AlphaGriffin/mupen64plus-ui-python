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
import pygame
import time
import shutil
import numpy as np
import tensorflow as tf
from PIL import Image
import ag.logging as log
from m64py.frontend.aicommon import AICommon
from PyQt5.QtCore import pyqtSlot, QTimer, QThread

VERSION = sys.version

# FIXME
INTRO =\
"""Recording Console by: AlphaGriffin.com.

Built in python 3.5.2
You are running: {0:2}
Step 1: Start a ROM and get past the menus and into the game and pause it.
Step 2: press the check if game is running button for non-async...
Step 3: Press record and go on to enjoy your game.
""".format(VERSION)

### PLEASE DEPRCIATE THIS SOON
class xpad(object):
    """ This conversion comes from the orginal TKart Demo """
    def __init__(self, options=None):
        self.joystick = None
        try:
            pygame.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        except Exception as e:
            print('unable to connect to Xbox Controller')
            pass

    def read(self):
        """Call polled for the xpad data."""
        pygame.event.pump()
        # left stick
        L_x_axis = self.joystick.get_axis(0)
        L_y_axis = self.joystick.get_axis(1)
        # need left stick click
        # right stick
        # R_x_axis = self.joystick.get_axis(2)
        # R_y_axis = self.joystick.get_axis(3)
        # need right stick click
        # need d-pad

        # game buttons
        a_btn = self.joystick.get_button(1)
        b_btn = self.joystick.get_button(2)
        # x_btn = self.joystick.get_button(2)
        # y_btn = self.joystick.get_button(3)

        # top buttons
        # lb = self.joystick.get_button(4)
        rb = self.joystick.get_button(5)

        # need start / select

        # need triggers /
        return [L_x_axis, L_y_axis, a_btn, b_btn, rb]

    def manual_override(self):
        """Take over from the AI."""
        pygame.event.pump()
        return self.joystick.get_button(4) == 1

    def press_joystick(self):
        print("press joystick")


        pass


class Player(AICommon):
    """AG_Recorder Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        log.debug("Recorder::__init__()")
        # init
        super().__init__(parent)
        self.setWorker(worker)   # get this from MUPEN core
        # self.pad = xpad() # get a controller instance
        self.query = TF_Query()
        # set up the blanks
        self.setWindowTitle('AG Recorder')
        self.selectorLabel.setText('Existing Save Folders:')
        self.inputLabel.setText('Save to:')
        self.actionButton.setEnabled(False)
        self.actionButton.setText('Record')
        self.checkButton.setEnabled(True)
        self.checkButton.setText('Check')
        self.check2Button.setEnabled(False)
        self.check2Button.setText('thing2')
        self.input.setEnabled(False)
        self.selector.setEnabled(False)

        # timer state
        self.runningTimer = False

        # booleans are good
        self.recording = False       # are we recording?
        self.recordStartedAt = None  # when did the recording start?
        self.game_on = False         # is there a game runnning?

        # preset some globals
        self.poll_time = None  # pep compliance...
        self.selectedSaveName = None
        self.path = ""
        self.check_game_name = ""
        self.padresult = ""
        self.model_dir = ""

        # startup
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
        self.startupTimer()

    def set_save_dir(self):
        """Sets the Input Field text"""
        name = self.getGame()
        name_path = os.path.join(self.work_dir, "training", name)
        if not os.path.isdir(name_path):
            print("path does not exist, creating it now: {}".format(
                   name_path))
            os.makedirs(name_path)
        self.print_console("Good Choice with {}, Good luck!".format(name))

        self.build_selector(name_path)

        l = len(os.listdir(name_path))
        path = "newGame_{}".format(l)
        msg = "Ready to Save in Directory:"
        self.print_console("{}\n{}".format(msg, os.path.join(name_path, path)))
        self.input.setText(os.path.join(name_path, path))
        self.actionButton.setEnabled(True)

    def build_selector(self, folder):
        """This populates the save folder list"""
        self.selector.clear()
        for i in sorted(os.listdir(folder)):
            x = "{}".format(i)
            self.selector.addItem(x)
        self.selector.addItem("Record a New Game")

    """DEPRICATED!
    def save_data(self, test=False):
        # Create data.csv - Timestamp, { 0.0, 0.0, 0, 0, 0 }
        paddle_read = self.pad.read()
        stamp = int(time.time() * 1000)
        y = ("{}:\t{}".format(stamp, paddle_read))
        if test is False:
            # make / open outfile
            outfileName = os.path.join(self.save_name, 'data.csv')
            print("{}".format(outfileName))
            outfile = open(outfileName, 'a')

            # write line
            outfile.write('{},{}\n'.format(stamp, ','.join(
                          map(str, paddle_read))))
            outfile.close()
        self.print_console(y)
    """

    @property
    def get_pad(self):
        return self.padresult

    def getGame(self):
        """Check if game has been selected."""
        x_test = self.check_game_name =\
            self.worker.core.rom_header.Name.decode(
                ).replace(" ", "_").lower()
        if x_test is not "":
            return x_test
        return "no_game"

    def startupTimer(self):
        """Start a timer if none is running."""
        # start game checker
        if self.runningTimer is False:
            self.print_console(
                "Start a Game to begin.")
            self.runningTimer = QTimer(self)
            # takes the pick and saves data
            self.runningTimer.timeout.connect(
                self.check_game)
            self.runningTimer.start(200)    # in millis

    def shutdownTimer(self):
        """Shuts down the timer(dialog hidden, etc.)."""
        # if not logic then #fkit
        if self.runningTimer is False:
            self.runningTimer.stop()
            self.runningTimer = False

    def check_game(self):
        """Check mupen worker.

        And see if hes working, called by runningTimer.
        """
        wasloaded = self.game_on
        self.worker.core_state_query(1)
        loaded = self.worker.state in [2, 3]
        self.game_on = loaded

        if not loaded:
            if wasloaded:
                self.actionButton.setEnabled(False)
            if self.recording:
                self.stop()
        if not wasloaded:
            if loaded:
                game_name = self.getGame()
                self.query.setup()
                self.print_console("{} is running.".format(
                    game_name
                ))
                model_dir = os.path.join(
                    self.work_dir, "model",
                    self.check_game_name)
                try:
                    model_dir_list = os.listdir(model_dir)
                    self.model_dir = os.path.join(
                        model_dir,
                        model_dir_list[0])
                except:
                    self.model_dir = None
                    pass
                self.shutdownTimer()
                self.check2Button.setEnabled(True)

    def load_model(self):
        """Loading model for selected game."""
        self.print_console("This model {}, could take a sec to load, be cool.".format(self.model_dir))
        try:
            self.query.load_model(self.model_dir)
            self.actionButton.setEnabled(True)
            return True
        except Exception as e:
            self.print_console("model not loading.")
            self.actionButton.setEnabled(False)
            return False

    def start_server(self):
        log.debug("start_server()")
        pid = os.getpid()
        time = datetime.now().isoformat(timespec='minutes')
        host = "127.0.0.1"
        port = 12345
        server = Sock_Server(host, port, pid)
        self.server_thread = ServerThread(target=server.start_server).start()
        self.serving = True
        return True

    def record(self):
        """Toggle game player."""
        self.print_console("Starting Recording")
        self.actionButton.setText('Stop')
        # start timer stuff
        self.poll_time = QTimer(self)
        self.poll_time.timeout.connect(
            self.get_and_del_image)
        self.poll_time.start(50)    # in millis
        # use shawns auto screenshoterator
        self.worker.toggle_autoshots()
        self.recording = True
        self.recordStartedAt = time.time()*1000.0

    def stop(self):
        """Stop capturing."""
        self.poll_time.stop()
        self.worker.toggle_autoshots()
        self.actionButton.setText('Record')

        elapsed = time.time()*1000.0 - self.recordStartedAt
        self.print_console(
            "Recording took {0:.2f} seconds".format(
                elapsed/1000.0))
        self.recordStartedAt = None
        self.recording = False

    def get_and_del_image(self):
        """Grab Screenshot and then delete it."""
        # self.print_console("Getting Image.")

        shot_dir = os.path.join(
            self.work_dir, "screenshot/")
        # self.print_console("about to list dir: {}".format(shot_dir))
        shot_dir_list = os.listdir(shot_dir)
        # self.print_console("got stuff: {}".format(shot_dir_list))
        if len(shot_dir_list) > 1:
            start_time = time.time()
            img = shot_dir_list[0]
            cur_image = os.path.join(shot_dir, img)
            try:
                # making numpy img first works better ... dont know why.
                numpy_image = self.prepare_image(cur_image)
                self.query.set_img(numpy_image)
                self.query.start()
                self.padresult = self.query.get_test
                self.print_console("Everything Worked. {}".format(
                    self.get_pad))
            except Exception as e:
                self.print_console("Failing Conversion")
                pass
            # self.print_console("Image: {}".format(
            #    numpy_image))
            mv_to = '/tmp/'
            # print("moving: {} -> {}".format(
            #    cur_image, mv_to))
            shutil.move(cur_image, mv_to)
            end_time = time.time()
            self.print_console("Frame Complete. Time: {0:.3f}".format(
                end_time - start_time))

    def prepare_image(self, img):
        """Resize to a tensorflow spec."""
        log.debug("prepare_image: {}".format(img))
        if os.path.isfile(img):
            pass
        else:
            self.print_console("Test Image is not found.")
            return False
        pil_image = Image.open(img)
        log.debug("pil_image: {}".format(pil_image))
        x = pil_image.resize((200, 66), Image.ANTIALIAS)
        log.debug("pil_image resized: {}".format(x))
        numpy_img = np.array(x)  # convert to numpy
        log.debug("numpy img created: {}".format(
            numpy_img.shape[:]))
        return numpy_img

    def show(self):
        """Default show command."""
        # this is not happening...
        self.startupTimer()
        super().show()

    def hide(self):
        """Stop recording on game close."""
        self.shutdownTimer()
        self.stop()
        super().hide()

    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Toggle record button."""
        if not self.recording:
            self.record()
        else:
            self.stop()

    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Check constitution of system."""
        self.check_game()
        self.print_console("Checking Record Readiness.")

    @pyqtSlot()
    def on_check2Button_clicked(self):
        """Test Button for pressing broken parts."""
        self.load_model()
        self.print_console("Model Loaded.")

    @pyqtSlot()
    def on_selector_itemSelectionChanged(self): pass

    @pyqtSlot()
    def closeEvent(self, event=False): pass


class TF_Query(QThread):
    def setup(self):
        self.test = 1
        print("Thread Setup Passed.")

    @property
    def get_test(self):
        return self.test

    def set_img(self, img):
        self.img = img

    def load_model(self, path):
        print("trying to load model")
        self.model_name = "/Mupen64plus"
        self.sess = tf.InteractiveSession()
        checkpoint_file = tf.train.latest_checkpoint(path)
        print("Checkpoint File: {}".format(checkpoint_file))
        meta_path = checkpoint_file + ".meta"
        saver = tf.train.import_meta_graph(meta_path)
        print("Initializing Graph.")
        self.sess.run(tf.global_variables_initializer())
        saver.restore(self.sess, checkpoint_file)
        print("Loading Saved Values.")
        self.x = tf.get_collection_ref('x_image')[0]
        self.k = tf.get_collection_ref('keep_prob')[0]
        self.y = tf.get_collection_ref('y')[0]
        debug = "input: {}\nkeep_prob: {}\nfinal layer: {}"
        print(debug.format(self.x, self.k, self.y))
        print("model successfully Loaded: {}".format(path))

    def run(self):
        feed_dict = {self.x: [self.img], self.k: 1.0}
        joystick = self.sess.run(self.y, feed_dict)[0]
        output = [
            int(joystick[0] * 80),
            int(joystick[1] * 80),
            int(round(joystick[2])),
            int(round(joystick[3])),
            int(round(joystick[4])),
            ]
        self.test += output
        #print(output)
        print("Thread {} Ran.{}".format(self.test, self.img))
        # cant return anything this way.
        # return 2
