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

import webbrowser
import traceback
from imp import reload
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialog
from m64py.utils import version_split
from m64py.ui.ai_ui import Ui_AIDashboard
from m64py.frontend.agerror import AGError
import ag.logging as log


class Deferred():
    """Deferred loading for AI Dashboard components."""

    def __init__(self, dashboard, tabname):
        """Initialize the class."""
        log.debug()

        self.loaded = False
        self.dashboard = dashboard
        self.tabname = tabname
        self.tabindex = -1

    def handleBackend(self, tabindex=-1):
        log.debug()
        force = False

        if tabindex >= 0 and self.tabindex == tabindex:
            force = True

        if self.loaded and not force:
            return True

        self.loaded = False
        self.dashboard.status.setText("Loading the " + self.tabname + " backend...")

        #if self.tabindex >= 0:
        #    self.dashboard.tabster.removeTab(self.tabindex)
        #    self.tabindex = self.dashboard.tabster.insertTab(
        #            self.tabindex, self.dashboard.loading, self.frontend,
        #            self.tabname + "...")
        #else:
        #    self.tabindex = self.dashboard.tabster.addTab(
        #            self.dashboard.loading, self.tabname + "...")

        try:
            log.debug("attempting to load backend")
            self.backend = self.loadBackend(force)

            self.dashboard.backendReady.emit(self, force)
            self.dashboard.status.setText("The " + self.tabname + " backend is ready.")
            return True

        except Exception:
            self.handleException()
            return False

    def loadBackend(self, force):
        """Subclass implemention."""
        pass

    def handleFrontend(self, force=False):
        log.debug()

        if self.loaded and not force:
            return True

        self.loaded = False

        try:
            log.debug("attempting to load frontend")
            self.frontend = self.loadFrontend(force)

            if self.backend is not None:
                self.backend.print = self.frontend.print_console

            if self.tabindex >= 0:
                self.dashboard.tabster.removeTab(self.tabindex)
                self.tabindex = self.dashboard.tabster.insertTab(
                        self.tabindex, self.frontend, self.tabname)
            else:
                self.tabindex = self.dashboard.tabster.addTab(
                        self.frontend, self.tabname)

            self.loaded = True
            return True

        except Exception:
            self.handleException()
            return False

    def loadFrontend(self, force):
        """Subclass implemention."""
        pass

    def handleException(self):
        log.error()

        err = AGError(self.dashboard, traceback.format_exc())
        name = "[!] " + self.tabname

        if self.tabindex >= 0:
            self.dashboard.tabster.removeTab(self.tabindex)
            self.dashboard.tabster.insertTab(self.tabindex, err, name)
        else:
            self.tabindex = self.dashboard.tabster.addTab(err, name)


class AIDashboard(QDialog, Ui_AIDashboard):
    """The Alpha Griffin Aritificial Intelligence Dashboard."""

    backendReady = pyqtSignal(Deferred, bool)

    def __init__(self, parent, worker, settings):
        """Initialize the dashboard.

        Args:
            parent (QDialog):       The window we belong to (usually mainwindow)
            worker (Worker):        Frontend worker thread which manages ROM state
            settings (Settings):    Instance of Settings dialog from mainwindow
        """

        log.info("Initializing Alpha Griffin Artificial Intelligence Dashboard")
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.parent = parent
        self.worker = worker
        self.settings = settings

        if log.level >= log.DEBUG:
            self.tabster.setTabsClosable(True)

        # check for required core version
        self.valid = False
        version = self.worker.core.plugin_get_version(self.worker.core.m64p,
                self.worker.core.core_path)
        if version:
            version = version[1]
            required = int('0x030000', 16)

            if version >= required:
                self.valid = True

        if not self.valid:
            log.error("Bad core version", found=version_split(version),
                    required=version_split(required))
            self.status.setText(
                    "Core version {} or higher required.".format(
                        version_split(required)))
            return

        # set up all the functional tabs for deferred load
        self.status.setText("Preparing the interface...")
        self.recorder = Recorder(self)
        self.processing = Processing(self)
        self.training = Training(self)
        self.player = Player(self)

        self.backends = BackendLoader(self)
        self.backendReady.connect(self.on_backendReady)

        #self.nextTabButton.setEnabled(True)
        self.status.setText("Ready (loading deferred).")

    def show(self):
        """Show this window and attempt to load any tabs not already loaded."""
        log.debug()
        super().show()
        if self.valid:
            self.backends.start()

    @pyqtSlot(Deferred, bool)
    def on_backendReady(self, component, force):
        log.debug("Backend is ready", component=component)
        component.handleFrontend(force)
        
        if self.backends.isFinished():
            self.status.setText("Ready.")

    @pyqtSlot()
    def on_website_clicked(self):
        """Open web browser to AlphaGriffin.com."""
        url = 'http://alphagriffin.com'
        log.info("Opening web browser", url=url)
        webbrowser.open(url)

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
        if not self.valid:
            return

        if self.backends.isFinished():
            self.backends.tabindex = index
            self.backends.start()
        else:
            log.debug("not ready yet")


class BackendLoader(QThread):
    def __init__(self, dashboard):
        QThread.__init__(self, dashboard)
        self.dashboard = dashboard
        self.tabindex = -1

    def run(self):
        dash = self.dashboard
        errs = 0
        
        if not dash.recorder.handleBackend(self.tabindex): errs += 1
        if not dash.processing.handleBackend(self.tabindex): errs += 1
        if not dash.training.handleBackend(self.tabindex): errs += 1
        if not dash.player.handleBackend(self.tabindex): errs += 1

        if errs > 1:
            dash.status.setText("{} components failed to load. Open the tabs with [!] for details.".format(errs))
        elif errs > 0:
            dash.status.setText("A component failed to load. Open the tab with [!] for details.")


class Recorder(Deferred):
    def __init__(self, dashboard):
        log.debug()
        Deferred.__init__(self, dashboard, "Record")

    def loadBackend(self, force):
        import m64py.ai.recorder as backend
        if force: reload(backend)
        return backend.Recorder()

    def loadFrontend(self, force):
        import m64py.frontend.recorder as frontend
        if force: reload(frontend)
        dash = self.dashboard
        return frontend.Recorder(dash, dash.status, dash.worker, self.backend)


class Processing(Deferred):
    def __init__(self, dashboard):
        log.debug()
        Deferred.__init__(self, dashboard, "Process")

    def loadBackend(self, force):
        import m64py.ai.processing as backend
        if force: reload(backend)
        return backend.Processing()

    def loadFrontend(self, force):
        import m64py.frontend.processing as frontend
        if force: reload(frontend)
        dash = self.dashboard
        return frontend.Processing(dash, dash.status, dash.worker, self.backend)


class Training(Deferred):
    def __init__(self, dashboard):
        log.debug()
        Deferred.__init__(self, dashboard, "Train")

    def loadBackend(self, force):
        import m64py.ai.trainer as backend
        if force: reload(backend)
        return backend.Trainer()

    def loadFrontend(self, force):
        import m64py.frontend.trainer as frontend
        if force: reload(frontend)
        dash = self.dashboard
        return frontend.Trainer(dash, dash.status, dash.worker, self.backend)


class Player(Deferred):
    def __init__(self, dashboard):
        log.debug()
        Deferred.__init__(self, dashboard, "Play")

    def loadBackend(self, force):
        return None

    def loadFrontend(self, force):
        import m64py.frontend.player as frontend
        if force: reload(frontend)
        dash = self.dashboard
        return frontend.Player(dash, dash.worker, dash.settings)

