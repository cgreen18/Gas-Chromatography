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
import yaml

class MainApp(gc_gui.GCFrame):
    def __init__(self, parent):
        with open('config.yaml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            self.options = data



        gc_gui.GCFrame.__init__(self, parent, data)
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
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, '&New')
        file_menu.Append(wx.ID_CLEAR, '&Clear')
        file_menu.Append(wx.ID_OPEN, '&Open')
        file_menu.Append(wx.ID_SAVE, '&Save')
        file_menu.Append(wx.ID_SAVEAS, '&Save as')
        file_menu.AppendSeparator()

        file_menu.Append(wx.ID_PRINT, '&Print')
        file_menu.AppendSeparator()

        file_item = file_menu.Append(wx.ID_EXIT, '&Quit' , 'Quit application')
        self.Bind(wx.EVT_MENU, self.on_quit,file_item)

        menubar.Append(file_menu,'&File')

        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_PAGE_SETUP, '&Settings')

        self.SetMenuBar(menubar)

    def on_quit(self , err):
        self.Close()

    def clear_curr_data(self, err):
        pass


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
