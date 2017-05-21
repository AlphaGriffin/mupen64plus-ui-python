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

import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QTextCursor
from m64py.ui.agblank_ui import Ui_AGBlank
import ag.logging as log


class AGBlank(QWidget, Ui_AGBlank):
    """Abstract class for the record/playback interfaces.

    You could add code here that all the interfaces that
    extend this class would find useful.
    """

    def __init__(self, parent=None, status=None):
        """Init an AGBlank PyQt5 page."""
        log.debug()
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.statusWidget = status
        self.work_dir = None
        self.worker = None
        self.root_dir = None

    def print_console(self, msg):
        """Print string to console."""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText("{}\n".format(msg))
        print(msg)

    def setWorker(self, worker, work_dir=None):
        """Take Global reference.

        Get Worker from main code and check the local
        Userdata folder.
        """
        log.debug()
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

    def status(self, msg):
        """Update status message."""
        if self.statusWidget is not None:
            self.statusWidget.setText(msg)
