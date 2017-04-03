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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from m64py.ui.ai_ui import Ui_AIDashboard
import traceback

from m64py.frontend.agerror import AGError

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

        self.status.setText("Loading the interface...")

        self.parent = parent
        self.worker = worker
        self.settings = settings

        try:
            from m64py.frontend.recorder import Recorder
            self.recorder = Recorder(self, self.worker)
            self.tabster.addTab(self.recorder, "Record")
        except Exception as e:
            log.error("Failed to load Recorder: {}".format(e))
            self.recorder = None
            self.tabster.addTab(AGError(self, traceback.format_exc()), "[!] Record")

        try:
            from m64py.frontend.processing import Processing
            self.processing = Processing(self, self.worker)
            self.tabster.addTab(self.processing, "Process")
        except Exception as e:
            log.error("Failed to load Processing: {}".format(e))
            self.processing = None
            self.tabster.addTab(AGError(self, traceback.format_exc()), "[!] Process")

        try:
            from m64py.frontend.trainer import Trainer
            self.trainer = Trainer(self, self.worker)
            self.tabster.addTab(self.trainer, "Train")
        except Exception as e:
            log.error("Failed to load Trainer: {}".format(e))
            self.trainer = None
            self.tabster.addTab(AGError(self, traceback.format_exc()), "[!] Train")

        try:
            from m64py.frontend.player import Player
            self.player = Player(self, self.worker, self.settings)
            self.tabster.addTab(self.player, "Play")
        except Exception as e:
            log.error("Failed to load Player: {}".format(e))
            self.player = None
            self.tabster.addTab(AGError(self, traceback.format_exc()), "[!] Play")

        self.nextTabButton.setEnabled(True)
        self.status.setText("Ready.")


    def show(self):
        """show this window"""
        super().show()
        log.debug("AIDashboard::show()")

    @pyqtSlot()
    def on_prevTabButton_clicked(self):
        index = self.tabster.currentIndex()
        self.tabster.setCurrentIndex(index-1)

    @pyqtSlot()
    def on_nextTabButton_clicked(self):
        index = self.tabster.currentIndex()
        self.tabster.setCurrentIndex(index+1)

    @pyqtSlot(int)
    def on_tabster_currentChanged(self, index):
        self.prevTabButton.setEnabled(index > 0)
        self.nextTabButton.setEnabled(index < self.tabster.count() - 1)

