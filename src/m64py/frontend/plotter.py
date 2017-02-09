# -*- coding: utf-8 -*-
# Author: AlphaGriffin <Alphagriffin.com>
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


from PyQt5.QtWidgets import QDialog#, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas # this is breaking it!
from matplotlib.figure import Figure
from m64py.ui.plotter_ui import Ui_Plotter
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtCore
import pygame

class xpad(object):
    """Example pygame controller read"""
    def __init__(self,options=None):
        try:
            pygame.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        except:
            print('unable to connect to Xbox Controller')
            
    def read(self):
        pygame.event.pump()
        
        # left stick
        L_x_axis = self.joystick.get_axis(0)
        L_y_axis = self.joystick.get_axis(1)
        # right stick
        #R_x_axis = self.joystick.get_axis(2)
        #R_y_axis = self.joystick.get_axis(3)
        # face buttons
        #x_btn = self.joystick.get_button(0)
        a_btn = self.joystick.get_button(1)
        b_btn = self.joystick.get_button(2)
        #y_btn = self.joystick.get_button(3)
        # top buttons
        rb = self.joystick.get_button(5)
        #return[L_x_axis,L_y_axis,R_x_axis,R_y_axis,x_btn,a_btn,b_btn,y_btn,rb]
        #return [x, y, a, b, rb]
        return [L_x_axis, L_y_axis, a_btn, b_btn, rb]
        
    def manual_override(self):
        pygame.event.pump()
        return self.joystick.get_button(4) == 1


class paddle_graph(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, layout=None, width=5, height=4, dpi=100):
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.controller = xpad()
        self.setParent(parent)
        layout.addWidget(self)
        self.setup_grapth()
        
        # Wait to turn the timer on until we need it, i.e. when the dialog is shown,
        #   otherwise the mainwindow isn't quite ready yet and things crash
        #self.timerOn()
        
        
    def setup_grapth(self):     
        self.plotMem = 50                                # how much data to keep on the plot
        self.plotData = [[0] * (5)] * self.plotMem       # mem storage for plot
        self.axes = self.fig.add_subplot(111)        
        #print("changes")
                
    def timerOn(self):
        """Starts a QTimer for paddle polling"""
        self.padTimer = QtCore.QTimer(self)
        self.padTimer.timeout.connect(self.update_figure)
        self.padTimer.start(100)
        
    def timerOff(self):
        """Stops the QTimer for paddle polling"""
        self.padTimer.stop()
        
    def update_figure(self):
        """This is called by the Timer Function"""
        self.controller_data = self.controller.read()
        self.plotData.append(self.controller_data) # adds to the end of the list
        self.plotData.pop(0) # remove the first item in the list, ie the oldest
        
        x = np.asarray(self.plotData)
        self.axes.plot(range(0,self.plotMem), x[:,0], 'r')
        self.axes.hold(True)
        self.axes.plot(range(0,self.plotMem), x[:,1], 'b')
        self.axes.plot(range(0,self.plotMem), x[:,2], 'g')
        self.axes.plot(range(0,self.plotMem), x[:,3], 'k')
        self.axes.plot(range(0,self.plotMem), x[:,4], 'y')
        self.axes.hold(False)
        self.draw()

class Plotter(QDialog, Ui_Plotter):
    """Construct from the .ui file"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.graph = paddle_graph(self.graph_widget, self.graph_layout, width=6, height=4, dpi=125)
    
    def show(self):
        """Do open window"""
        super().show()
        self.graph.timerOn()
        
    def hide(self):
        """Do Close Window"""
        super().hide()
        self.graph.timerOff()