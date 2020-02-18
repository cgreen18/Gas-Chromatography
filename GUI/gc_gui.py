"""
Title: gc_gui.py
Author: Conor Green & Matt McPartlan
Description: Highest level script of wxPython based GUI application to perform data acquisition and display.
Usage: Call from command line as main
Version:
1.0 - November 24 2019 - Initial creation. All dependencies left in the script: will later be split into various scripts that are imported.
1.1 - November 24 2019 - Implements numpy and plotting to window. Uses random numbers
"""

import wx

import numpy as np
import wx.lib.plot as plot

### Classes for the script

# Class to define this specific GUI
class GC_GUI(wx.Frame):

    def __init__(self, *args , **kwargs ):

        self.defaults = { 'window_size':(800,600) , 'title' : 'LMU EE GC DAQ App'}

        self.frame = super(GC_GUI,self).__init__(*args , **kwargs)


        self.setup()
        self.Centre()

    def setup(self):
        #self.frame = wx.Frame(None, title="wx.lib.plot", id=-1, size=(410, 340))

        print(type(self))
        print(type(self.frame))

        menubar = wx.MenuBar()
        file_menu = wx.Menu()

        self.panel = wx.Panel(self.frame,-1)

        plotter = plot.PlotCanvas(self.panel)

        plotter.SetEnableZoom(True)

        # list of (x,y) data point tuples
        data = [(1,2), (2,3), (3,5), (4,6), (5,8), (6,8), (12,10), (13,4)]
        # draw points as a line
        line = plot.PolyLine(data, colour='red', width=1)
        # also draw markers, default colour is black and size is 2
        # other shapes 'circle', 'cross', 'square', 'dot', 'plus'
        marker = plot.PolyMarker(data, marker='triangle')
        # set up text, axis and draw
        gc = plot.PlotGraphics([line, marker], 'Line/Marker Graph', 'x axis', 'y axis')
        plotter.Draw(gc, xAxis=(0,15), yAxis=(0,15))

        self.Show(True)

        self.button1 = wx.Button(self.panel,-1,'start', (8,72), (75,23))
        self.button1.SetFont(wx.Font(8.25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, 'Microsoft Sans Serif'))
        self.button1.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))

        self.Bind(wx.EVT_BUTTON,self.start_button_clicked,self.button1)


        file_menu.Append(wx.ID_NEW, '&New')
        file_menu.Append(wx.ID_OPEN, '&Open')
        file_menu.Append(wx.ID_SAVE, '&Save')
        file_menu.AppendSeparator()
        file_item = file_menu.Append(wx.ID_EXIT, '&Quit' , 'Quit application')




        menubar.Append(file_menu,'&File')

        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit,file_item)


        self.SetSize(self.defaults['window_size'])
        self.SetTitle(self.defaults['title'])
        self.Centre()


    def OnQuit(self , err):
        self.Close()

    def start_button_clicked(self, err):
        print('worx')
### Methods for the script

def main():
    app = wx.App()

    gc_gui = GC_GUI(None)


    gc_gui.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
