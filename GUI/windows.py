'''


'''

import numpy as np

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

import wx
import wx.lib.plot as plot

import os
import codecs, json
import time

from gc_class import GC

import threading
from threading import Thread

import serial


# SplitterWindow
class GCSplitter(wx.SplitterWindow):
    '''
    parent is GCFrame
    '''
    def __init__(self, parent):
        ops = parent.options
        fs = ops['frame_size']
        wx.SplitterWindow.__init__(self, parent, id=wx.ID_ANY,pos=wx.DefaultPosition , size=fs, style = wx.SP_BORDER, name='Diode Based Gas Chromatography' )
        self.options = ops

        self.parent = parent

    def create_fonts(self):
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(self.options['BODY_FONT_SIZE'])
        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(self.options['HEADER_FONT_SIZE'])

        return {'font':font,'header_font':header_font}



#DirectoryWindow(s)
class DirectoryWindow(wx.Frame):
    def __init__(self, parent, data):
        self.parent = parent
        self.cwd = os.getcwd()

        self.options = data
        self.fonts = self.create_fonts()

        self.create_frame()
        self.update_cwd()

    def create_fonts(self):
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(self.options['BODY_FONT_SIZE'])
        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(self.options['HEADER_FONT_SIZE'])

        return {'font':font,'header_font':header_font}

    def create_frame(self):
        wx.Frame.__init__ ( self, self.parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = (600,600), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((-1,self.options['EXTRA_SPACE']))

        nav_hbox = self.create_nav_hbox()

        vbox.Add(nav_hbox, border = self.options['BORDER'])

        self.list_box = self.create_cwd_listbox()

        vbox.Add(self.list_box, border = self.options['BORDER'])

        name_hbox = self.create_name_and_enter()
        vbox.Add(name_hbox)

        self.SetSizer(vbox)
        self.Centre()
        self.Show()

    def create_nav_hbox(self):
        nav_menu_hbox = wx.BoxSizer(wx.HORIZONTAL)
        nav_menu_hbox.Add((self.options['EXTRA_SPACE'],-1))

        bmp = wx.Bitmap(imdir + '/btn_back_im_20p.png', wx.BITMAP_TYPE_ANY)

        self.btn_bck = wx.BitmapButton(self, id=wx.ID_ANY,bitmap=bmp, size = (45,40))
        self.Bind(wx.EVT_BUTTON, self.bckbtn_click_evt, self.btn_bck)

        nav_menu_hbox.Add(self.btn_bck)
        #nav_menu_hbox.Add((EXTRA_SPACE, -1))
        self.tc_cwd = wx.TextCtrl(self, value = self.cwd, pos=wx.DefaultPosition, size=(500,40))
        self.tc_cwd.SetFont(self.fonts['font'])

        nav_menu_hbox.Add(self.tc_cwd, proportion=1, border = self.options['BORDER'])

        return nav_menu_hbox

    def create_cwd_listbox(self):
        self.cwd_list = os.listdir(self.cwd)

        self.list_box = wx.ListBox(self, size = (550,400), choices = self.cwd_list, style=wx.LB_SINGLE)

        self.Bind(wx.EVT_LISTBOX_DCLICK, self.basic_cwdlist_dclick_evt, self.list_box)

        return self.list_box

    def create_name_and_enter(self):
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(self.parent.options['BODY_FONT_SIZE'])

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.tc_name = wx.TextCtrl(self, value = wx.EmptyString, pos = wx.DefaultPosition, size = (400,40))
        self.tc_name.SetFont(font)

        hbox.Add(self.tc_name, proportion=1, border= self.parent.options['BORDER'])


        self.btn_entr = wx.Button(self, id=wx.ID_ANY, label=wx.EmptyString, size = (150,40))
        self.Bind(wx.EVT_BUTTON, self.entrbtn_click_evt, self.btn_entr)

        hbox.Add(self.btn_entr)

        return hbox

    def entrbtn_click_evt(self, event):
        pass

    def basic_cwdlist_dclick_evt(self, event):
        index = event.GetSelection()
        choice = self.cwd_list[index]

        is_dir = os.path.isdir(choice)
        if is_dir:
            try:
                os.chdir(choice)
                self.cwd = os.getcwd()
                self.cwd_list = os.listdir(self.cwd)
                self.update_cwd()
                return

            except Exception:
                pass

        filename, extension = os.path.splitext(choice)

        self.update_namectl_to_dclick(choice)

        self.spec_cwdlist_dclick_evt(choice, filename, extension)

    def spec_cwdlist_dclick_evt(self,  choice, filename, extension):
        pass

    def bckbtn_click_evt(self, event):
        os.chdir('..')
        self.cwd = os.getcwd()
        self.cwd_list = os.listdir(self.cwd)
        self.update_cwd()

    def update_cwd(self):
        self.list_box.Clear()
        self.list_box.Append(self.cwd_list)

        self.tc_cwd.Clear()
        self.tc_cwd.write(self.cwd)

        self.Show()

    def update_namectl_to_dclick(self, choice):
        self.tc_name.Clear()
        self.tc_name.write(choice)

class SaveasWindow(DirectoryWindow):
    def __init__(self, parent, data):
        str = 'Save As'
        DirectoryWindow.__init__(self,parent, data)
        self.SetTitle(str)
        self.btn_entr.SetLabel(str)

    def entrbtn_click_evt(self, event):
        pass

class SaveasGC(SaveasWindow):
    def __init__(self, parent, data):
        SaveasWindow.__init__(self, parent, data)

        self.SetTitle('Save Session As GC')
        self.btn_entr.SetLabel('Save as .gc')
        #Get important parameters
        self.curr_data = self.parent.get_curr_data()

    def entrbtn_click_evt(self, event):
        name = self.tc_name.GetValue()
        self.save_gc(name)

    def save_gc(self, name):
        date = strftime('%d %m %Y', localtime())
        time = strftime('%H:%M:%S',localtime())

        curr_data = self.jsonify_data(self.curr_data)

        print(curr_data)

        if name[-3:] != '.gc':
            name = name + '.gc'

        # Format of JSON .gc filetype
        curr_session = {
        'Date' : date ,
        'Time' : time ,
        'Current Data' : curr_data ,
         'Previous Data': None
        }

        with codecs.open(name , 'w', encoding='utf-8') as json_file:
            json.dump(curr_session, json_file, separators =(',',':'),indent=4)

    '''
    dict(numpys)->dict(lists)
    '''
    def jsonify_data(self, numpy_dict):
        json_dict = {}
        json_dict.update((key,val.tolist()) for key,val in numpy_dict.items()  )

        return json_dict

    '''
    dict(lists)->dict(numpys)
    '''
    def reverse_jsonify(self, json_dict):
        numpy_dict = {}
        numpy_dict.update((key, np.array(val)) for key,val in json_dict.items() )
        return numpy_dict

class SaveasPNG(SaveasWindow):
    def __init__(self, parent, data):
        SaveasWindow.__init__(self, parent, data)

        self.SetTitle('Save Current Figure As PNG')
        self.btn_entr.SetLabel('Save as .png')
        self.figure = self.parent.get_figure()

    def entrbtn_click_evt(self, event):
        name = self.tc_name.GetValue()
        self.save_png(name)

    def save_png(self, name):
        if name[-4:] == '.png':
            self.figure.savefig(name )
        else:
            self.figure.savefig(name + '.png')

class SaveasJPG(SaveasWindow):
    def __init__(self, parent, data):
        SaveasWindow.__init__(self, parent, data)

        self.SetTitle('Save Current Figure As JPEG')
        self.btn_entr.SetLabel('Save as .jpg')
        self.figure = self.parent.get_figure()

    def entrbtn_click_evt(self, event):
        name = self.tc_name.GetValue()
        self.save_jpg(name)

    def save_jpg(self, name):
        if name[-4:] == '.jpg':
            self.figure.savefig(name)
        else:
            self.figure.savefig(name + '.jpg')

class OpenWindow(DirectoryWindow):
    def __init__(self, parent, data):
        str = 'Open GC File'
        super().__init__( parent, data)
        self.SetTitle(Open)
        self.btn_entr.SetLabel(str)

    def spec_cwdlist_dclick_evt(self,  choice, filename, extension):
        pass
