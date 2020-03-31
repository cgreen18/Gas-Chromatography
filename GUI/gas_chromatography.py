'''
Name: gas_chromatography.py
Authors: Conor Green and Matt McPartlan
Description: Highest abstraction of GC GUI interface. Will be initially called from bash upon startup of Raspberry Pi.
Usage: Call as main
Version:
1.0 - 26 January 2020 - Initial creation. Skeleton to outline work for later
1.1 - 20 February 2020 - Import and create gc_class Gas_Chrom object.
1.2 - 30 March 2020 - Complete overhaul. Utilizes frame and panel classes created in gc_gui and smashes them together using the SplitterWindow.
'''

import wx
import gc_gui

class MainApp(gc_gui.GCFrame):
    def __init__(self, parent, **kwargs):
        self.options = {'size':(1200,600) , 'config_panel_width':300}
        self.options.update(kwargs)

        gc_gui.GCFrame.__init__(self, parent, size = self.options['size'])

        self.split_vert()

    def split_vert(self):
        splitter = wx.SplitterWindow(self, wx.ID_ANY, style = wx.SP_BORDER, size = self.options['size'])

        self.panel_detector = DetectorPanel(splitter)
        self.panel_config = ControlPanel(splitter)

        splitter.SplitVertically(self.panel_config , self.panel_detector, 300)# self.options['config_panel_width'])

        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        #self.GetSizer().Add(splitter, 1, wx.EXPAND)

class DetectorPanel(gc_gui.DetectorPanel):
    def __init__(self, parent):
        gc_gui.DetectorPanel.__init__(self, parent)
        self.parent = parent

class ControlPanel(gc_gui.ConfigPanel):
    def __init__(self, parent):
        gc_gui.ConfigPanel.__init__(self, parent)
        self.parent = parent


def main():
    app = wx.App()
    window = MainApp(None)
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
