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
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QTextCursor
from m64py.utils import need_dir
from m64py.ui.aicommon_ui import Ui_AICommon
import ag.logging as log


class AICommon(QWidget, Ui_AICommon):
    """Abstract class for the record/playback interfaces.

    You could add code here that all the components that
    extend this class would find useful.
    """

    def __init__(self, parent=None, status=None):
        """Init an AICommon PyQt5 page."""
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

    def setWorker(self, worker, work_dir):
        """Set Mupen worker and prepare working directory."""
        log.debug()
        self.worker = worker

        self.root_dir = self.worker.core.config.get_path("UserData")
        log.info("root dir set to: {}".format(self.root_dir))

        self.work_dir = os.path.join(self.root_dir, work_dir)
        need_dir(self.work_dir)
        log.info("work dir set to: {}".format(self.work_dir))

    def status(self, msg):
        """Update status message."""
        log.info(msg)
        if self.statusWidget is not None:
            self.statusWidget.setText(msg)

