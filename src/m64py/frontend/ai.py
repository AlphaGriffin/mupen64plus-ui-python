# -*- coding: utf-8 -*-
# Author: SAW @ AlphaGriffin <Alphagriffin.com>
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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from m64py.ui.ai_ui import Ui_AIDashboard
import webbrowser

from m64py.frontend.recorder import Recorder
from m64py.frontend.trainer import Trainer
from m64py.frontend.processing import Processing
from m64py.frontend.player import Player

import ag.logging as log

#
# The Alpha Griffin Aritificial Intelligence Dashboard
#

class AIDashboard(QDialog, Ui_AIDashboard):
    def __init__(self, parent, worker, settings):
        """ @param parent   QDialog (mainwindow)
            @param worker   Mupen worker object
            @param settings Settings dialog instance from mainwindow """

        log.info("Initializing Alpha Griffin Artificial Intelligence Dashboard")
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.parent = parent
        self.worker = worker
        self.settings = settings

        #log.debug("record: {}".format(self.record))
        #self.record = Recorder(self.parent, self.worker)
        #self.record.setObjectName("record")

        self.recorder = Recorder(self, self.worker)
        self.tabster.addTab(self.recorder, "Record")

        self.trainer = Trainer(self, self.worker)
        self.tabster.addTab(self.trainer, "Train")

        self.processing = Processing(self, self.worker)
        self.tabster.addTab(self.processing, "Process")

        self.player = Player(self, self.worker, self.settings)
        self.tabster.addTab(self.player, "Play")



    def show(self):
        """show this window"""
        super().show()
        log.debug("AIDashboard::show()")

        #self.record.show()
        #self.retranslateUi(AIDashboard)

#    @pyqtSlot()
#    def on_website_clicked(self):
#        """Open web browser to AlphaGriffin.com."""
#        webbrowser.open('http://alphagriffin.com')
