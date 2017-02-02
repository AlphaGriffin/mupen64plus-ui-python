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


from PyQt5.QtWidgets import QDialog
from m64py.ui.agblank_ui import Ui_AGBlank

# Abstract class for the record/playback interfaces
#
# You could add code here that all the interfaces that extend this class
# would find useful.

class AGBlank(QDialog, Ui_AGBlank):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

#    @pyqtSlot()
#    def on_actionRecording_Console_triggered(self):
#        """Shows recorder dialog."""
#        recorder.show()




# Subclasses might create a member variable of their own:
#    
#agblank = AGBlank_YourSubclass()
