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
import numpy as np
from PIL import Image
from m64py.core.defs import Buttons
import ag.logging as log


class Processing():
    """The image processing.

    This will be used by both the Process and Playback
    Modules for conversion of images for Tensorflow.
    """

    def __init__(self, folders=""):
        self.folders = folders

    def print(self, msg):
        print(msg)

    def doIt(self, load_dir, folders, saveDir, currentGame):
        """Take care of all processing."""
        log.debug()

        if not os.path.isdir(saveDir):
            self.print("Creating folder: {}".format(saveDir))
            os.mkdir(saveDir)
        saveDir = os.path.join(saveDir, currentGame)
        if not os.path.isdir(saveDir):
            self.print("Creating folder: {}".format(saveDir))
            os.mkdir(saveDir)
        datasetIndex = len(os.listdir(saveDir))
        dataset_x = []
        dataset_y = []
        datasetFilename = "{}_dataset_{}".format(
                currentGame, datasetIndex)
        self.print("#############################################")
        self.print("# Processing Game folders to dataset")
        self.print("# Game Name: {}".format(currentGame))
        self.print("# Dataset Path: {}".format(saveDir))
        self.print("# Number of saves to process: {}".format(
                len(folders)))
        self.print("#############################################")

        # for each folder given...
        for i in folders:
            current_path = os.path.join(load_dir, i)
            self.print(
                "# Processing folder: {}".format(
                    current_path))
            self.print(
                "# Step 1: Assert #imgs == #labels")
            labels, imgs = self.gamepadImageMatcher(current_path)
            log.info("Input and Image matching completed",
                     inputs=len(labels),
                     images=len(imgs))
            dataset_y.append(labels)  # BOOM!
            self.print(
                "# Step 2: Convert img to BW np array of (x,y)")
            for image in imgs:
                img = self.prepare_image(
                    os.path.join(current_path, image))
                dataset_x.append(img)

        self.print(
            "# Step 3: Save files...\n\t{}.npz".format(
                datasetFilename))
        dataset_x = np.asarray(dataset_x)
        dataset_y = np.concatenate(dataset_y)
        # super_set = [dataset_x, dataset_y]
        self.print(
            "# To Dir:\t{}".format(saveDir))
        # DEPRICATED.
        # np.save(os.path.join(saveDir, datasetFilename_x), dataset_x)
        # np.save(os.path.join(saveDir, datasetFilename_y), dataset_y)
        np.savez(os.path.join(saveDir, datasetFilename),
                 images=dataset_x,
                 labels=dataset_y)
        self.print("# Finished preparing dataset")

    @staticmethod
    def make_BW(rgb):
        """The "rec601 luma" algorithm to compute 8-bit greyscale."""
        return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

    def prepare_image(self, img, makeBW=False):
        """Resize the image to a standard size."""
        pil_image = Image.open(img)
        x = pil_image.resize((200, 66), Image.ANTIALIAS)
        numpy_img = np.array(x)
        if makeBW:
            numpy_img = self.make_BW(numpy_img)
        return numpy_img

    def gamepadImageMatcher(self, path):
        """Match gamepad data rows to images based on timestamps.

        Params: A path with timestamped pictures and a
                timestamped .csv of varying lenghs.
        Returns: two arrays of matched length img, labels.
        """

        # Open input data for reading
        #   FIXME: support more than player 0
        csv_path = os.path.join(path, "controller0.dat")
        csv_io = open(csv_path, 'r')

        # Convert to a true array
        csv = []
        for line in csv_io:
            # Convert the compact controller data to an array of the inputs we
            # are interested in
            rawdata = [item.strip() for item in line.split(',')]

            if len(rawdata) == 2:
                data = []
                data.append(rawdata[0])  # timestamp

                buttons = Buttons()
                buttons.value = int(rawdata[1], 16)  # hex data

                data.append(buttons.bits.X_AXIS)
                data.append(buttons.bits.Y_AXIS)
                data.append(buttons.bits.A_BUTTON)
                data.append(buttons.bits.B_BUTTON)
                data.append(buttons.bits.R_TRIG)

                csv.append(data)
            else:
                log.error("Bad data in controller input log", line=csv_io)

        if not csv:
            # print ("CSV HAS NO DATA")
            return None, None

        # Get list of images in directory and sort it
        all_files = os.listdir(path)
        images = []
        for filename in all_files:
            if filename.endswith('.png'):
                images.append(filename)
        images = sorted(images)

        if not images:
            # print ("FOUND NO IMAGES");
            return None, None

        # We're going to build up 2 arrays of matching size:
        keep_csv = []
        keep_images = []

        # Prime the pump (queue)...
        prev_line = csv.pop(0)
        prev_csvtime = int(prev_line[0])

        while images:
            imgfile = images[0]
            # Get image time:
            #     Cut off the "gamename-" from the front and the ".png"
            hyphen = imgfile.rfind('-')  # Get last index of '-'
            if hyphen < 0:
                break
            imgtime = int(imgfile[hyphen+1:-4])  # cut it out!
            lastKeptWasImage = False  # Did we last keep an image, or a line?
            if imgtime > prev_csvtime:
                keep_images.append(imgfile)
                del images[0]
                lastKeptWasImage = True

                # We just kept an image, so we need to keep a
                # corresponding input row too
                while csv:
                    line = csv.pop(0)
                    csvtime = int(line[0])

                    if csvtime >= imgtime:
                        # We overshot the input queue... ready to
                        # keep the previous data line
                        # truncate  the timestamp
                        keep_csv.append(prev_line[1:])
                        lastKeptWasImage = False

                        prev_line = line
                        prev_csvtime = csvtime

                        if csvtime >= imgtime:
                            break

                    if not csv:
                        if lastKeptWasImage:
                            # truncate off the timestamp
                            keep_csv.append(prev_line[1:])
                        break

            else:
                del images[0]
        return keep_csv, keep_images

