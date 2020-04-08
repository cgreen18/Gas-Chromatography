'''
Name: gas_chromatography.py
Authors: Conor Green and Matt McPartlan
Description: Highest abstraction of GC GUI interface. Will be initially called from bash upon startup of Raspberry Pi.
Usage: Call as main
Version:
1.0 - 26 January 2020 - Initial creation. Skeleton to outline work for later
1.1 - 20 February 2020 - Import and create gc_class Gas_Chrom object.
1.2 - 30 March 2020 - Complete overhaul. Utilizes frame and panel classes created in gc_gui and smashes them together using the SplitterWindow.
1.3 - 30 March 2020 - Added Save As window that navigates directories and updates listbox.
1.4 - 31 March 2020 - Added Open window, similar to Save As. Both inherit new window class.
'''

import wx
import yaml
import os

import gc_gui

'''
self - MainApp object
param: self.options - the UI defeaults and current settings
param: self.parent - the parent wxPython object, in this case None (main call of MainApp(None))
'''
class MainApp(gc_gui.GCFrame):
    def __init__(self, parent):
        with open('config.yaml') as f:
            options = yaml.load(f, Loader=yaml.FullLoader)
            self.options = options

        gc_gui.GCFrame.__init__(self, parent, self.options)

        self.parent = parent


def main():
    app = wx.App()
    window = MainApp(None)
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
