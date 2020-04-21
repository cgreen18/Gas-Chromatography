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
1.4 - 31 March 2020 - Save current figure as .png or .jpg
1.5 - 21 April 2020 - FINALLY got threading working.
"""

import numpy as np
from numpy import arange, sin, pi

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
from time import localtime, strftime
import time

from gc_class import Gas_Chrom as GC

import threading
from threading import Thread
import multiprocessing as mp

from ctypes import Structure, c_float

imdir = 'images'

## TODO: Prompt keyobard when typing in temperature

# Frames
class GCFrame(wx.Frame):
    def __init__(self, parent, optiondict):
        self.constants = {'BODY_FONT_SIZE': 11, 'HEADER_FONT_SIZE':18,'EXTRA_SPACE':10, 'BORDER':10}
        self.options = {'frame_size':(800,400), 'sash_size':300, 'data_samp_rate':5,
                        'epsilon_time':0.001, 'plot_refresh_rate':2, 'single_ended':True}
        self.options.update(self.constants)

        self.options.update(optiondict)

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = self.options['DEFAULT_FRAME_SIZE'], style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.build_figure_()

        se = self.options['single_ended']
        self.gc = GC(se)
        self.parent = parent

    def __del__(self):
        pass

    def main(self):
        pass

    def get_figure(self):
        return self.panel_detector.get_figure()

    def get_curr_data(self):
        return self.gc.get_curr_data()

    # gc_class methods
    def update_curr_data(self):
        pass

    def on_play_btn(self):
        rr = self.options['data_samp_rate']
        sp = 1 / rr
        ep = self.options['epsilon_time']

        data_arr = np.zeros((self.gc.dims, 1))

        self.curr_data = data_arr
        self.curr_data_lock = threading.Lock()

        self.gc_lock = threading.Lock()
        self.gc_cond = threading.Condition(self.gc_lock)

        self.data_rover_thread = GCThread(self.gc, self.gc_cond, args = ( sp, ep ) )

        rsp = self.options['plot_refresh_rate']

        self.receiver_thread = GCReceiver(self, self.gc, self.gc_cond, args = ( rsp, ep ))

        self.data_rover_thread.start()
        self.receiver_thread.start()

        self.running= True


    def on_stop_btn(self):
        self.stop_data_coll()

    def stop_data_coll(self):

        self.receiver_thread.stop()

        self.receiver_thread.join()

        print('rec join')

        self.data_rover_thread.stop()

        self.data_rover_thread.join()

        print('data join')


        self.running = False

    def on_plot(self):
        if self.running:
            self.stop_data_coll()

        self.panel_detector.update_curr_data()
        self.panel_detector.draw()


    # Formatting
    def build_figure_(self):
        self.split_vert_()
        self.set_up_menu_bar_()

    def split_vert_(self):
        splitter = GCSplitter(self)

        self.panel_detector = DetectorPanel(splitter)
        self.panel_config = ControlPanel(splitter)

        splitter.SplitVertically(self.panel_config , self.panel_detector, self.options['sash_size'])

        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        self.GetSizer().Add(splitter, 1, wx.EXPAND)

    def set_up_menu_bar_(self):
        menubar = GCMenuBar(self)
        self.SetMenuBar(menubar)

    # Menu events
    def on_quit(self , err):
        self.Close()

    def on_saveas(self, err):
        saveas_gc_window = SaveasGC( self, self.options)

    def on_open(self, err):
        open_window = OpenWindow(self, self.options)

    def on_png_save(self, err):
        saveas_png_window = SaveasPNG(self, self.options)

    def on_jpg_save(self, err):
        saveas_jpg_window = SaveasJPG(self, self.options)

class GCPlotter(Thread):

    def __init__(self):
        pass

class GCReceiver(Thread):

    def __init__(self, frame, gc, condition, *args, **kwargs):
        super(GCReceiver, self).__init__()

        self.frame = frame
        self.gc = gc

        self.sp = kwargs['args'][0]
        self.ep = kwargs['args'][1]

        self._stop_event = threading.Event()

        self.gc_cond = condition

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        sampling_period = self.sp
        epsilon = self.ep

        t_last = time.time()
        while not self._stop_event.is_set():
            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.01)
                t_curr = time.time()

            t_last = t_curr
            with self.gc_cond:
                val = self.gc_cond.wait(1)

                if val:
                  print("notification received about item production...")

                  #self.gc_cond.acquire()
                  print('gc_cond acquired')

                  with self.frame.curr_data_lock:
                      print('acquired')
                      self.frame.curr_data = np.copy(self.gc.curr_data)

                else:
                  print("waiting timeout...")

class GCThread(Thread):
    def __init__(self, gc, condition, *args, **kwargs):
        super(GCThread, self).__init__()

        self.sp = kwargs['args'][0]
        self.ep = kwargs['args'][1]
        self.gc = gc
        self._stop_event = threading.Event()

        self.thread_data = np.zeros((gc.dims, 1))

        self.condition = condition
        self.avail = False

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def is_avail(self):
        return self.avail

    def run(self):
        t_last = time.time()

        sampling_period = self.sp
        epsilon = self.ep

        while not self._stop_event.is_set():
            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.01)
                t_curr = time.time()

            with self.condition:
                v = self.gc.get_voltage()
                dt = t_curr - t_last
                t = t_curr
                t_last = t_curr

                new = np.array((v,dt,t)).reshape(3,1)
                self.gc.curr_data = np.append(self.gc.curr_data, new, axis=1)
                print('new daata')
                self.condition.notify_all()

        print('done running')

# SplitterWindow
class GCSplitter(wx.SplitterWindow):
    '''
    parent is GCFrame
    '''
    def __init__(self, parent):
        self.options = parent.options
        self.parent = parent
        wx.SplitterWindow.__init__(self, parent, id=wx.ID_ANY,pos=wx.DefaultPosition , size=self.options['frame_size'], style = wx.SP_BORDER, name='Diode Based Gas Chromatography' )

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

#Panels
class DetectorPanel(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        self.gcframe = parent.parent

        self.options = {'BODY_FONT_SIZE': 11, 'HEADER_FONT_SIZE':18,'EXTRA_SPACE':10, 'BORDER':10}
        self.fonts = self.create_fonts()

        wx.Panel.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL)

        self.create_panel()


    def create_panel(self):
        f = self.fonts['font']
        hf = self.fonts['header_font']
        b = self.options['BORDER']
        es = self.options['EXTRA_SPACE']
        bfs = self.options['BODY_FONT_SIZE']

        vbox = wx.BoxSizer(wx.VERTICAL)

        str_det = wx.StaticText(self, label = 'Detector')
        str_det.SetFont(hf)

        vbox.Add(str_det, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border = b)

        vbox.Add((-1,es))



        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.vbox2 = wx.BoxSizer(wx.VERTICAL)

        hbox2 = self.create_control_box()

        self.vbox2.Add(hbox2, border=b)
        self.vbox2.Add((-1,20))

        self.create_plot_btn_()
        self.create_clr_btn_()


        hbox.Add(self.vbox2, border = b)

        hbox.Add((es, -1))

        self.create_figure_()

        hbox.Add(self.canvas)

        vbox.Add(hbox, border = b)
        self.SetSizer(vbox)
        self.Fit()

    def create_plot_btn_(self):
        f = self.fonts['font']
        b = self.options['BORDER']
        es = self.options['EXTRA_SPACE']


        self.btn_plot = wx.Button(self, label = 'plot', size = (200,50))
        self.btn_plot.SetFont(f)
        self.btn_plot.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))

        #self.Bind(wx.EVT_BUTTON, self.plot_btn_evt,self.btn_plot)

        self.vbox2.Add(self.btn_plot, border= b)
        self.vbox2.Add((-1,es))

    def create_clr_btn_(self):
        f = self.fonts['font']
        b = self.options['BORDER']
        es = self.options['EXTRA_SPACE']


        self.btn_clr = wx.Button(self, label = 'clear', size = (200,50))
        self.btn_clr.SetFont(f)
        self.btn_clr.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))

        self.Bind(wx.EVT_BUTTON,self.clear_plot_btn_evt,self.btn_clr)

        self.vbox2.Add(self.btn_clr, border= b)
        self.vbox2.Add((-1,es))

    def create_fonts(self):
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(self.options['BODY_FONT_SIZE'])
        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(self.options['HEADER_FONT_SIZE'])

        return {'font':font,'header_font':header_font}

    def create_figure_(self):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

    def create_control_box(self):

        b = self.options['BORDER']
        es = self.options['EXTRA_SPACE']

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.Bitmap(imdir + '/play_btn_20p.png',wx.BITMAP_TYPE_ANY)
        self.btn_ply = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))
        self.Bind(wx.EVT_BUTTON, self.ply_btn_evt, self.btn_ply)

        bmp = wx.Bitmap(imdir + '/paus_btn_20p.png',wx.BITMAP_TYPE_ANY)
        btn_paus = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))

        bmp = wx.Bitmap(imdir + '/stop_btn_20p.png',wx.BITMAP_TYPE_ANY)
        self.btn_stp = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))
        self.Bind(wx.EVT_BUTTON, self.stp_btn_evt, self.btn_stp)

        hbox.Add(self.btn_ply, border = b)
        hbox.Add((es,-1))
        hbox.Add(btn_paus, border =b)
        hbox.Add((es,-1))
        hbox.Add(self.btn_stp, border =b)
        hbox.Add((es,-1))

        return hbox

    def draw(self):
        self.axes.plot(self.curr_data[0], self.curr_data[1])
        self.canvas.draw()

    def ply_btn_evt(self, event):
        self.gcframe.on_play_btn()

    def stp_btn_evt(self, event):
        self.gcframe.on_stop_btn()

    def plot_btn_evt(self, event):
        pass
        # self.gcframe.plot_btn()
        # self.update_curr_data()
        # self.draw()

    def update_curr_data(self):
        self.curr_data = self.gcframe.curr_data

    def clear_plot_btn_evt(self, event):
        self.axes.cla()
        self.canvas.draw()

    def get_figure(self):
        return self.figure

    def get_curr_data(self):
        return self.curr_data

    def __del__(self):
        pass

class ControlPanel( wx.Panel ):
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

        grapher_menu.Append(wx.ID_ANY, '&Edit Axes')

        grapher_menu.AppendSeparator()

        grapher_menu.Append(wx.ID_ANY, '&Save Image')

        graph_menu_saveim = wx.Menu()
        png_save = graph_menu_saveim.Append(wx.ID_ANY, '&.png')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_png_save, png_save)

        jpg_save = graph_menu_saveim.Append(wx.ID_ANY,'&.jpg')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_jpg_save, jpg_save)

        grapher_menu.Append(wx.ID_ANY, '&Save Image As...', graph_menu_saveim)

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

        item_open = file_menu.Append(wx.ID_OPEN, '&Open')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_open, item_open)

        file_menu.AppendSeparator()

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
