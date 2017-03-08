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
from m64py.ui.agerror_ui import Ui_AGError
from PyQt5.QtGui import QTextCursor
import os

import ag.logging as log

class AGError(QWidget, Ui_AGError):
    def __init__(self, parent, details):
        log.debug("AGError::__init__()")
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.details.setPlainText(details)

