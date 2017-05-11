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


from PyQt5.QtWidgets import QWidget
from m64py.ui.agblank_ui import Ui_AGBlank
from PyQt5.QtGui import QTextCursor
import os

import ag.logging as log

# Abstract class for the record/playback interfaces
#
# You could add code here that all the interfaces that extend this class
# would find useful.

class AGBlank(QWidget, Ui_AGBlank):
    def __init__(self, parent=None):
        log.debug("AGBlank::__init__()")
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.work_dir = None

    def print_console(self, msg):
        """Takes a String and prints to console"""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText("{}\n".format(msg))
        print(msg)

    def setWorker(self, worker, work_dir=None):
        """Get Worker from main code and check the local Userdata folder"""
        log.debug("AGBlank::setWorker()")
        self.worker = worker
        self.root_dir = self.worker.core.config.get_path("UserData")
        log.info("root dir set to: {}".format(self.root_dir))

        if work_dir:
            self.work_dir = os.path.join(self.root_dir, work_dir)
        else:
            # for backwards-compatibility / failsafe default
            #   subclass should set work_dir to a subfolder of root_dir
            self.work_dir = self.root_dir
        log.info("work dir set to: {}".format(self.work_dir))


#    @pyqtSlot()
#    def on_actionRecording_Console_triggered(self):
#        """Shows recorder dialog."""
#        recorder.show()




# Subclasses might create a member variable of their own:
#
#agblank = AGBlank_YourSubclass()
