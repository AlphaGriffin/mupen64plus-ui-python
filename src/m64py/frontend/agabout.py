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

import webbrowser
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from m64py.ui.agabout_ui import Ui_AGAbout


class AGAbout(QDialog, Ui_AGAbout):
    """Open web browser to AlphaGriffin.com."""

    def __init__(self, parent=None):
        """Open web browser to AlphaGriffin.com."""
        QDialog.__init__(self, parent)
        self.setupUi(self)

    @staticmethod
    @pyqtSlot()
    def on_website_clicked():
        """Open web browser to AlphaGriffin.com."""
        webbrowser.open('http://alphagriffin.com')
        return True
