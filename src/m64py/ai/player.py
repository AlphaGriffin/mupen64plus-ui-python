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

import os 
import numpy as np
import tensorflow as tf
from PIL import Image
from PIL import ImageFile
from m64py.core.defs import Buttons
import ag.logging as log

ImageFile.LOAD_TRUNCATED_IMAGES = True  # FIXME?



class Player(object):
    """Actual connection to TensorFlow subsystem and image processing"""

    def __init__(self, autoshots_path='.'):
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

        images = sorted(images)
        file = images[0]
        log.debug("found file: {}".format(file))

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
                #int(0), # START BUTTON
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

