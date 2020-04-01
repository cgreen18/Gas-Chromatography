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
import gc_gui
import yaml
import os

class MainApp(gc_gui.GCFrame):
    def __init__(self, parent):
        with open('config.yaml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            self.options = data


        gc_gui.GCFrame.__init__(self, parent, self.options)
        #self becomes a GCFrame

        self.split_vert()
        self.panel_detector.draw()

        self.set_up_menu_bar()

    def split_vert(self):

        splitter = wx.SplitterWindow(self, id=wx.ID_ANY,pos=wx.DefaultPosition , size=self.options['frame_size'], style = wx.SP_BORDER, name='Diode Based Gas Chromatography' )

        splitter.options = self.options

        self.panel_detector = DetectorPanel(splitter)
        self.panel_config = ControlPanel(splitter)

        splitter.SplitVertically(self.panel_config , self.panel_detector, self.options['sash_size'])

        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        self.GetSizer().Add(splitter, 1, wx.EXPAND)

    def set_up_menu_bar(self):
        menubar = gc_gui.GCMenuBar(self)

        self.SetMenuBar(menubar)

    # Menu events
    def on_quit(self , err):
        self.Close()

    def on_saveas(self, err):
        saveasWindow = SaveasWindow(self, self.options)

    def on_open(self, err):
        openWindow = OpenWindow(self, self.options)

class SaveasWindow(gc_gui.DirectoryWindow):
    def __init__(self, parent, data):
        super().__init__(parent, data)
        self.SetTitle('Save As')

class OpenWindow(gc_gui.DirectoryWindow):
    def __init__(self, parent, data):
        super().__init__( parent, data)
        self.SetTitle('Open')

    def spec_cwdlist_dclick_evt(self,  choice, filename, extension):
        pass

class DetectorPanel(gc_gui.DetectorPanel):
    def __init__(self, parent):
        gc_gui.DetectorPanel.__init__(self, parent)
        self.parent = parent

    def clear_curr_data(self):
        self.clear_curr_data()

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
