"""
Title: gc_gui.py
Author: Conor Green & Matt McPartlan
Description: Highest level script of wxPython based GUI application to perform data acquisition and display.
Usage: Instantiate classes GCFrame, DetectorPanel, and ConfigPanel from gas_chromatography.py
Version:
1.0 - November 24 2019 - Initial creation. All dependencies left in the script: will later be split into various scripts that are imported.
1.1 - November 24 2019 - Implements numpy and plotting to window. Uses random numbers
1.2 - 31 March 2020 - Old gas_chromatography.py -> gc_gui.py. This script defines the frame and panel classes that are put together in gas_chromatography.py. As of currently, it plots an example sin curve in the plotter but interfacing with the ADS1115 will be implemented when this is tested on a Raspberry Pi.
1.3 - 31 March 2020 - Added images to buttons. Added more menu options.
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

#Frames
class GCFrame(wx.Frame):
    def __init__(self, parent, optiondict):
        self.constants = {'BODY_FONT_SIZE': 11, 'HEADER_FONT_SIZE':18,'EXTRA_SPACE':10, 'BORDER':10}

        self.options = {'frame_size':(800,400), 'sash_size':300}
        self.options.update(self.constants)
        self.options.update(optiondict)

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = self.options['frame_size'], style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
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
        self.parent = parent

        BODY_FONT_SIZE = self.parent.options['BODY_FONT_SIZE']
        HEADER_FONT_SIZE = self.parent.options['HEADER_FONT_SIZE']
        EXTRA_SPACE = self.parent.options['EXTRA_SPACE']
        BORDER = self.parent.options['BORDER']


        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(HEADER_FONT_SIZE)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(BODY_FONT_SIZE)

        wx.Panel.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL)

        vbox = wx.BoxSizer(wx.VERTICAL)

        str_det = wx.StaticText(self, label = 'Detector')
        str_det.SetFont(header_font)

        vbox.Add(str_det, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border = BORDER)

        vbox.Add((-1,EXTRA_SPACE))



        hbox = wx.BoxSizer(wx.HORIZONTAL)


        vbox2 = wx.BoxSizer(wx.VERTICAL)


        bmp = wx.Bitmap('images/play_btn_20p.png',wx.BITMAP_TYPE_ANY)
        btn_ply = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))

        bmp = wx.Bitmap('images/paus_btn_20p.png',wx.BITMAP_TYPE_ANY)
        btn_paus = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))

        bmp = wx.Bitmap('images/stop_btn_20p.png',wx.BITMAP_TYPE_ANY)
        btn_stp = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))


        vbox2.Add(btn_ply, border = BORDER)
        vbox2.Add((-1,EXTRA_SPACE))
        vbox2.Add(btn_paus, border = BORDER)
        vbox2.Add((-1,EXTRA_SPACE))
        vbox2.Add(btn_stp, border = BORDER)
        vbox2.Add((-1,EXTRA_SPACE))

        self.btn_clr = wx.Button(self, label = 'clear', size = (200,50))
        self.btn_clr.SetFont(font)
        self.btn_clr.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))

        self.Bind(wx.EVT_BUTTON,self.clear_plot_btn,self.btn_clr)



        vbox2.Add(self.btn_clr, border= BORDER)
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
        self.canvas.draw()

    def clear_plot_btn(self, event):
        self.axes.cla()

        self.canvas.draw()

    def __del__(self):
        pass

class ConfigPanel( wx.Panel ):

    def __init__( self, parent ):
        self.parent = parent

        BODY_FONT_SIZE = self.parent.options['BODY_FONT_SIZE']
        HEADER_FONT_SIZE = self.parent.options['HEADER_FONT_SIZE']
        EXTRA_SPACE = self.parent.options['EXTRA_SPACE']
        BORDER = self.parent.options['BORDER']


        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )

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

# Menus
class GCMenuBar(wx.MenuBar):

    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent = parent


        file_menu = self.create_file_menu()
        self.Append(file_menu,'&File')

        edit_menu = self.create_edit_menu()
        self.Append(edit_menu,'&Edit')

        data_menu = self.create_data_menu()
        self.Append(data_menu,'&Data')

        grapher_menu = self.create_grapher_menu()
        self.Append(grapher_menu, '&Grapher')

    def create_grapher_menu(self):
        grapher_menu = wx.Menu()

        grapher_menu.Append(wx.ID_ANY, '&Edit Axes...')

        return grapher_menu

    def create_data_menu(self):
        data_menu = wx.Menu()

        data_menu.Append(wx.ID_ANY, '&Previous Set')
        data_menu.Append(wx.ID_ANY, '&Operations...')

        return data_menu

    def create_edit_menu(self):
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_PAGE_SETUP, '&Settings')

        return edit_menu

    def create_file_menu(self):
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, '&New')
        file_menu.Append(wx.ID_CLEAR, '&Clear')
        file_menu.Append(wx.ID_OPEN, '&Open')
        file_menu.Append(wx.ID_SAVE, '&Save')

        item_saveas =file_menu.Append( wx.ID_SAVEAS, '&Save as' )

        self.parent.Bind(wx.EVT_MENU, self.parent.on_saveas, item_saveas)

        file_menu.AppendSeparator()

        file_menu.Append(wx.ID_PRINT, '&Print')
        file_menu.AppendSeparator()

        item_quit = file_menu.Append(wx.ID_EXIT, '&Quit' , 'Quit application')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_quit,item_quit)

        return file_menu

if __name__ == '__main__':
    pass
