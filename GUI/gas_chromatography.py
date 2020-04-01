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


        print(self)
        print(parent)
        print(gc_gui.GCFrame)

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

        item_saveas =file_menu.Append( wx.ID_SAVEAS, '&Save as' )
        self.Bind(wx.EVT_MENU, self.on_saveas, item_saveas)

        file_menu.AppendSeparator()

        file_menu.Append(wx.ID_PRINT, '&Print')
        file_menu.AppendSeparator()

        item_quit = file_menu.Append(wx.ID_EXIT, '&Quit' , 'Quit application')
        self.Bind(wx.EVT_MENU, self.on_quit,item_quit)

        menubar.Append(file_menu,'&File')

        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_PAGE_SETUP, '&Settings')

        self.SetMenuBar(menubar)

    def on_quit(self , err):
        self.Close()

    def on_saveas(self, err):
        print("here")
        saveasWindow = SaveasWindow(self, self.options)
        #saveasWindow.show()

class SaveasWindow(wx.Frame):
    def __init__(self, parent, data):
        self.parent = parent
        self.title = 'Save As'
        self.cwd = os.getcwd()


        self.create_frame()
        self.update_cwd_menu()

    def create_frame(self):
        BODY_FONT_SIZE = self.parent.options['BODY_FONT_SIZE']
        HEADER_FONT_SIZE = self.parent.options['HEADER_FONT_SIZE']
        EXTRA_SPACE = self.parent.options['EXTRA_SPACE']
        BORDER = self.parent.options['BORDER']

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(BODY_FONT_SIZE)
        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(HEADER_FONT_SIZE)

        wx.Frame.__init__ ( self, self.parent, id = wx.ID_ANY, title = self.title, pos = wx.DefaultPosition, size = (600,400), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        #self.SetBackgroundColour(wx.Colour(100,100,100))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((-1,EXTRA_SPACE))


        nav_menu_hbox = wx.BoxSizer(wx.HORIZONTAL)
        nav_menu_hbox.Add((EXTRA_SPACE,-1))

        bmp = wx.Bitmap('images/btn_back_im_20p.png', wx.BITMAP_TYPE_ANY)

        self.btn_bck = wx.BitmapButton(self, id=wx.ID_ANY,bitmap=bmp, size = (45,40))
        self.Bind(wx.EVT_BUTTON, self.bckbtn_click_evt, self.btn_bck)

        nav_menu_hbox.Add(self.btn_bck)
        #nav_menu_hbox.Add((EXTRA_SPACE, -1))
        tc_cwd = wx.TextCtrl(self, value = self.cwd, pos=wx.DefaultPosition, size=(500,40))
        tc_cwd.SetFont(font)

        nav_menu_hbox.Add(tc_cwd, proportion=1, border = BORDER)

        vbox.Add(nav_menu_hbox, border = BORDER)

        self.cwd_list = os.listdir(self.cwd)

        self.list_box = wx.ListBox(self, size = (-1,400), choices = self.cwd_list, style=wx.LB_SINGLE)

        self.Bind(wx.EVT_LISTBOX_DCLICK, self.cdwlist_dclick_evt, self.list_box)

        hbox_buf = wx.BoxSizer(wx.HORIZONTAL)
        hbox_buf.Add((45+EXTRA_SPACE,-1))

        hbox_buf.Add(self.list_box,border=BORDER)

        vbox.Add(hbox_buf)

        self.SetSizer(vbox)
        self.Centre()
        self.Show()

    def cdwlist_dclick_evt(self, event):
        index = event.GetSelection()
        choice = self.cwd_list[index]

        try:
            os.chdir(choice)
            self.cwd = os.getcwd()
            self.cwd_list = os.listdir(self.cwd)
            self.update_cwd_menu()

        except Exception:
            pass

    def bckbtn_click_evt(self, event):
        os.chdir('..')
        self.cwd = os.getcwd()
        self.cwd_list = os.listdir(self.cwd)
        self.update_cwd_menu()

    def update_cwd_menu(self):
        print("to updatea")
        print(self.cwd_list)
        self.list_box.Clear()
        self.list_box.Append(self.cwd_list)

        #self.list_box.choices = self.cwd_list
        self.Show()



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
