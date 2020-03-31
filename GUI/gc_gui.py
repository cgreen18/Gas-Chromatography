"""
Title: gc_gui.py
Author: Conor Green & Matt McPartlan
Description: Highest level script of wxPython based GUI application to perform data acquisition and display.
Usage: Call from command line as main
Version:
1.0 - November 24 2019 - Initial creation. All dependencies left in the script: will later be split into various scripts that are imported.
1.1 - November 24 2019 - Implements numpy and plotting to window. Uses random numbers
"""

import numpy as np
from numpy import arange, sin, pi

import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure


import wx
import wx.lib.plot as plot
### Classes for the script


#Frames
class GCFrame(wx.Frame):

    def __init__(self, parent, **kwargs):
        self.options = {'size':(800,400)}

        self.options.update(kwargs)

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = self.options['size'], style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )


    def __del__(self):
        pass

    def OnQuit(self , err):
        self.Close()

    def main(self):
        pass


#Panels
class DetectorPanel(wx.Panel):
    def __init__(self, parent):
        HEADER_FONT_SIZE = 16
        EXTRA_SPACE = 25
        BORDER = 10

        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(HEADER_FONT_SIZE)

        wx.Panel.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL)

        vbox = wx.BoxSizer(wx.VERTICAL)

        str_det = wx.StaticText(self, label = 'Detector')
        str_det.SetFont(header_font)

        vbox.Add(str_det, border = BORDER)

        vbox.Add((-1,EXTRA_SPACE))



        hbox = wx.BoxSizer(wx.HORIZONTAL)


        vbox2 = wx.BoxSizer(wx.VERTICAL)



        btn_ply = wx.Button(self, label = '=>', size = (50,50))
        btn_paus = wx.Button(self, label = 'II', size = (50,50))
        btn_stp = wx.Button(self, label = '[]', size = (50,50))

        vbox2.Add(btn_ply, border = BORDER)
        vbox2.Add((-1,EXTRA_SPACE))
        vbox2.Add(btn_paus, border = BORDER)
        vbox2.Add((-1,EXTRA_SPACE))
        vbox2.Add(btn_stp, border = BORDER)
        vbox2.Add((-1,EXTRA_SPACE))

        btn_clr = wx.Button(self, label = 'clear', size = (200,50))

        vbox2.Add(btn_clr, border= BORDER)
        vbox2.Add((-1,EXTRA_SPACE))


        hbox.Add(vbox2, border = BORDER)

        hbox.Add((EXTRA_SPACE, -1))

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)


        hbox.Add(self.canvas)

        vbox.Add(hbox, border = BORDER)
        self.SetSizer(vbox)
        self.Fit()


    def draw(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)

    def __del__(self):
        pass

class ConfigPanel( wx.Panel ):

    def __init__( self, parent ):
        BODY_FONT_SIZE = 11
        HEADER_FONT_SIZE = 16
        BORDER = 10
        EXTRA_SPACE = 25


        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 100,100 ), style = wx.TAB_TRAVERSAL )

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(BODY_FONT_SIZE)
        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(HEADER_FONT_SIZE)

        vbox = wx.BoxSizer(wx.VERTICAL)

        #Temperature
        str_temp = wx.StaticText(self, label = 'Temperature')
        str_temp.SetFont(header_font)


        vbox.Add(str_temp, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,border =BORDER)


        vbox.Add((-1,EXTRA_SPACE))

        #Oven temp
        hbox_ov_set = wx.BoxSizer(wx.HORIZONTAL)
        str_ov_set = wx.StaticText(self,label='Set Oven Temp.: ')
        str_ov_set.SetFont(font)
        hbox_ov_set.Add(str_ov_set)

        tc_ov_set = wx.TextCtrl(self)
        hbox_ov_set.Add(tc_ov_set, proportion=1)


        vbox.Add(hbox_ov_set, flag=wx.LEFT|wx.TOP,border =BORDER)



        hbox_ov_fdbk = wx.BoxSizer(wx.HORIZONTAL)
        str_ov_fdbk = wx.StaticText(self, label = 'Oven Temp. Reading: ')
        str_ov_fdbk.SetFont(font)
        hbox_ov_fdbk.Add(str_ov_fdbk)

        str_ov_fdbk_val = wx.StaticText(self, label = 'N/A')
        str_ov_fdbk_val.SetFont(font)
        hbox_ov_fdbk.Add(str_ov_fdbk_val)


        vbox.Add(hbox_ov_fdbk, flag=wx.LEFT|wx.TOP,border =BORDER)


        vbox.Add((-1,EXTRA_SPACE))

        #Detector temp
        hbox_det_set = wx.BoxSizer(wx.HORIZONTAL)
        str_det_set = wx.StaticText(self, label = 'Set Detector Temp.: ')
        str_det_set.SetFont(font)
        hbox_det_set.Add(str_det_set)

        tc_det_set = wx.TextCtrl(self)
        hbox_det_set.Add(tc_det_set, proportion = 1)

        vbox.Add(hbox_det_set, flag=wx.LEFT|wx.TOP,border =BORDER)

        hbox_det_fdbk = wx.BoxSizer(wx.HORIZONTAL)
        str_det_fdbk = wx.StaticText(self, label = 'Detector Temp. Reading: ')
        str_det_fdbk.SetFont(font)
        hbox_det_fdbk.Add(str_det_fdbk)

        str_det_fdbk_val = wx.StaticText(self, label = 'N/A')
        str_det_fdbk_val.SetFont(font)
        hbox_det_fdbk.Add(str_det_fdbk_val)

        vbox.Add(hbox_det_fdbk, flag=wx.LEFT|wx.TOP,border =BORDER)


        self.SetSizer(vbox)

    def __del__( self ):
        pass
        # Virtual event handlers, overide them in your derived class
    def changeIntroPanel( self, event ):
        event.Skip()
