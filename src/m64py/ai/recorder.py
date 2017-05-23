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
import sys
import time
import shutil
from m64py.utils import version_split
import ag.logging as log


class Recorder():

    def __init__(self):
        self.root_dir = None
        self.save_name = None

    def print(self, msg):
        print(msg)

    def get_controllers(self):
        """Move all the controller input logs to the save_dir."""
        input_dir = os.path.join(self.root_dir, "input/")

        count = self.move_all_files(input_dir)

        if count > 0:
            self.print(
                "Got {} input logs, moved to {}".format(
                    count, self.save_name))
        else:
            self.checkButton.setEnabled(True)
            self.print("No Inputs Saved")

    def get_images(self):
        """Move all the screenshots to the current save_dir."""
        shot_dir = os.path.join(self.root_dir,
                                "screenshot/")
        count = self.move_all_files(shot_dir)
        if count > 0:
            self.print(
                "Got {} images, moved to {}".format(
                    count, self.save_name))
        else:
            self.checkButton.setEnabled(True)
            self.print("No ScreenShots Saved")

    def move_all_files(self, from_dir):
        log.debug("about to list dir: {}".format(from_dir))
        files = os.listdir(from_dir)
        log.debug("got stuff: {}".format(files))
        if len(files) > 0:
            for file in files:
                mv_from = os.path.join(from_dir, file)
                mv_to = self.save_name
                log.debug("moving", file=mv_from, to=mv_to)
                shutil.move(mv_from, mv_to)

            return len(files)

        else:
            self.checkButton.setEnabled(True)
            self.print("No ScreenShots Saved")



