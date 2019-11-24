'''
Title: gc_gui.py
Author: Conor Green & Matt McPartlan
Description: Highest level script of wxPython based GUI application to perform data acquisition and display.
Usage: Call from command line as main
Version:
1.0 - November 24 2019 - Initial creation. All dependencies left in the script: will later be split into various scripts that are imported.
'''

import wx


### Classes for the script

# Class to define this specific GUI
class GC_GUI(wx.Frame):

    def __init__(self, *args , **kwargs ):

        self.defaults = { 'window_size':(800,600) , title = 'LMU EE GC DAQ App'}

        super(GC_GUI,self).__init__(*args , **kwargs)

        self.setup()

    def setup(self):
        
        self.Centre()


### Methods for the script

def main():
    app = wx.App()

    main_menu = GC_GUI(None ,title = defaults['title'], size = defaults['window_size'])
    frame.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
