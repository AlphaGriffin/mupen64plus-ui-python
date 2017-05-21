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

from imp import reload
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from m64py.ui.ai_ui import Ui_AIDashboard
from m64py.frontend.agdeferred import AGDeferred
import ag.logging as log


class AIDashboard(QDialog, Ui_AIDashboard):
    """The Alpha Griffin Aritificial Intelligence Dashboard."""

    def __init__(self, parent, worker, settings):
        """Alphagriffin Module Loader.

        @param parent   QDialog (mainwindow)
        @param worker   Mupen worker object
        @param settings Settings dialog instance from mainwindow
        """
        log.info("Initializing Alpha Griffin Artificial Intelligence Dashboard")
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.status.setText("Loading the interface...")
        self.parent = parent
        self.worker = worker
        self.settings = settings

        if log.level >= log.DEBUG:
            self.tabster.setTabsClosable(True)

        # set up all the functional tabs for deferred load
        self.drecorder = DRecorder(self)
        self.dprocessing = DProcessing(self)
        self.dtrainer = DTrainer(self)
        self.dplayer = DPlayer(self)
        self.dtester = DTester(self)  # FIXME just testing

        self.nextTabButton.setEnabled(True)
        self.status.setText("Ready (loading deferred).")


    def show(self):
        """show this window and attempt to load any tabs not already loaded"""
        log.debug()
        super().show()

        errs = 0
        if not self.drecorder.check(): errs += 1
        if not self.dprocessing.check(): errs += 1
        if not self.dtrainer.check(): errs += 1
        if not self.dplayer.check(): errs += 1
        if not self.dtester.check(): errs += 1

        if errs > 1:
            self.status.setText("{} components failed to load. Open the tabs with [!] for details.".format(errs))
        elif errs > 0:
            self.status.setText("A component failed to load. Open the tab with [!] for details.")


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

    @pyqtSlot(int)
    def on_tabster_tabBarDoubleClicked(self, index):
        self.on_tabster_tabCloseRequested(index)

    @pyqtSlot(int)
    def on_tabster_tabCloseRequested(self, index):
        #self.tabster.removeTab(index)

        self.drecorder.reload(index)
        self.dprocessing.reload(index)
        self.dtrainer.reload(index)
        self.dplayer.reload(index)
        self.dtester.reload(index)

        self.tabster.setCurrentIndex(index)


class DRecorder(AGDeferred):
    def __init__(self, dashboard):
        log.debug()
        AGDeferred.__init__(self, dashboard, "Record")

    def load(self):
        import m64py.frontend.recorder as frontend
        reload(frontend)
        recorder = frontend.Recorder(self.dashboard, self.dashboard.status, self.dashboard.worker)
        self.dashboard.recorder = recorder
        return recorder


class DProcessing(AGDeferred):
    def __init__(self, dashboard):
        log.debug()
        AGDeferred.__init__(self, dashboard, "Process")

    def load(self):
        import m64py.frontend.processing as frontend
        reload(frontend)
        processing = frontend.Processing(self.dashboard, self.dashboard.status, self.dashboard.worker)
        self.dashboard.processing = processing
        return processing


class DTrainer(AGDeferred):
    def __init__(self, dashboard):
        log.debug()
        AGDeferred.__init__(self, dashboard, "Train")

    def load(self):
        import m64py.frontend.trainer as frontend
        reload(frontend)
        trainer = frontend.Trainer(self.dashboard, self.dashboard.status, self.dashboard.worker)
        trainer.process.start()
        self.dashboard.trainer = trainer
        return trainer


class DPlayer(AGDeferred):
    def __init__(self, dashboard):
        log.debug()
        AGDeferred.__init__(self, dashboard, "Play")

    def load(self):
        import m64py.frontend.player as frontend
        reload(frontend)
        player = frontend.Player(self.dashboard, self.dashboard.worker, self.dashboard.settings)
        self.dashboard.player = player
        return player


# FIXME: just testing
class DTester(AGDeferred):
    def __init__(self, dashboard):
        log.debug()
        AGDeferred.__init__(self, dashboard, "Play (TEST)")

    def load(self):
        import m64py.frontend.recorder_player as frontend
        reload(frontend)
        player = frontend.Player(self.dashboard, self.dashboard.worker)
        self.dashboard.player = player
        return player
