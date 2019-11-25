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

        self.defaults = { 'window_size':(800,600) , 'title' : 'LMU EE GC DAQ App'}

        super(GC_GUI,self).__init__(*args , **kwargs)

        self.setup()

    def setup(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_item = file_menu.Append(wx.ID_EXIT, 'Quit' , 'Quit application')
        menubar.Append(file_menu,'&File') #Underlines F for hotkey
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit,file_item)


        self.SetSize(self.defaults['window_size'])
        self.SetTitle(self.defaults['title'])
        self.Centre()


    def OnQuit(self , err):
        self.Close()

### Methods for the script

def main():
    app = wx.App()

    gc_gui = GC_GUI(None)
    gc_gui.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
