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


import ag.logging as log
import traceback


from m64py.frontend.agerror import AGError

class AGDeferred():
    def __init__(self, dashboard, tabname):
        log.debug()

        self.loaded = False
        self.dashboard = dashboard
        self.tabname = tabname
        self.tabindex = -1

    def check(self):
        """Load ourselves by calling load() (only if we need to) while gracefully handling errors."""
        log.debug()

        if self.loaded:
            return True

        self.dashboard.status.setText("Loading the " + self.tabname + " interface...")
        try:
            log.debug("attempting to load")
            widget = self.load()

            if self.tabindex >= 0:
                self.dashboard.tabster.removeTab(self.tabindex)
                self.tabindex = self.dashboard.tabster.insertTab(self.tabindex, widget, self.tabname)
            else:
                self.tabindex = self.dashboard.tabster.addTab(widget, self.tabname)

            self.dashboard.status.setText("Ready.")
            self.loaded = True
            return True

        except Exception:
            log.error()

            err = AGError(self.dashboard, traceback.format_exc())
            name = "[!] " + self.tabname

            if self.tabindex >= 0:
                self.dashboard.tabster.removeTab(self.tabindex)
                self.dashboard.tabster.insertTab(self.tabindex, err, name)
            else:
                self.tabindex = self.dashboard.tabster.addTab(err, name)

            return False

    def reload(self, index):
        """Reload only if we are at the specified tab index."""
        if self.tabindex == index:
            log.debug(index=index)
            self.loaded = False
            return self.check()

    def load(self):
        """Subclasses implement this function to actually do something."""
        pass

