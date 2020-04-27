'''
Title: gc_gui.py
Author: Conor Green & Matt McPartlan
Description: Mid-level abstraction of GUI application to perform data acquisition and display. Defines GUI and threading classes and instantiates GC object.
Usage: Instantiate GCFrame object from gas_chromatography.py
Version (mainly for final report later):
1.0 - November 24 2019 - Initial creation. All dependencies left in the script: will later be split into various scripts that are imported.
1.1 - November 24 2019 - Implements numpy and plotting to window. Uses random numbers
1.2 - 31 March 2020 - Old gas_chromatography.py -> gc_gui.py. This script defines the frame and panel classes that are put together in gas_chromatography.py. As of currently, it plots an example sin curve in the plotter but interfacing with the ADS1115 will be implemented when this is tested on a Raspberry Pi.
1.3 - 31 March 2020 - Added images to buttons. Added more menu options.
1.4 - 31 March 2020 - Save current figure as .png or .jpg
1.5 - 21 April 2020 - FINALLY got threading working.
2.0 - 21 April 2020 - Version 2.0 successfully graphs live data with play button, ...
                            graphs it live, saves images and .gc files, and clears.
                            Basic, minimum GC supporting software.
2.1 - 22 April 2020 - Serial connection with Arduino through temperature thread, which updates the text feedback.
                        Commands not yet implemented.
2.2 - 22 April 2020 - Works with updated gc_class and lock.
2.3 - 22 April 2020 - Added functions on voltage in menu bar.
2.4 - 24 April 2020 - Stable. Correctly increments run_number and stores data in prev_data.
                        Menu data functions: normalize, integrate, and clean time all work as intended.
                        Menu grapher function: fill almost works
3.0 - 24 April 2020 - Arduino serial interface. Temperature control and feedback thread. Normalize, integrate, and clean time menu functions.
3.1 - 25 April 2020 - Open .gc file will set current and previous data to the loaded file.
3.2 - 25 April 2020 - Opening .gc file works.
3.3 - 25 April 2020 - Label peaks works.
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

imdir = '.images'

# Frames
class GCFrame(wx.Frame):
    # self is MainApp(GCFrame)
    # parent is None
    def __init__(self, parent, user_options):
        self.__version__ = '3.3'
        self.__authors__ = 'Conor Green and Matt McPartlan'

        self.establish_options_(user_options)
        self.parent = parent

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = self.options['frame_size'], style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.build_figure_()

        self.establish_serial_conn_()
        self.ser_lock = threading.Lock()

        # Requires serial cofnnection self.ser_conn
        self.temp_thread_running = False
        self.establish_temperature_thread_()

        # including curr_data_frame and curr_data_frame_lock
        self.curr_data_frame_lock = threading.Lock()
        self.establish_GC_()

        _dims = self.gc.get_dims()
        self.curr_data_frame = np.zeros((_dims, 0))
        self.update_curr_data_()

        self.prev_data = []
        self.run_number = 0

        self.data_running = False
        self.data_paused = False


    '''
    Building functions
    '''
    def get_arduino_port(self):
        possible = [x for x in os.listdir('/dev/') if 'ACM' in x]

        if len(possible) == 0:
            print("Error: No ACM ports found to connect to Arduino.")
            print("Attempting on default ttyACM0 for now.")
            possible.append('ttyACM0')
        elif len(possible) != 1:
            print("Error: Multiple possible ACM ports to connect Arduino.")
            print("Defaulting to '/dev/ttyACM0'")
            possible[0] = 'ttyACM0'

        local = possible[0]
        string = '/dev/' + possible[0]

        return string

    def establish_serial_conn_(self):
        bd = self.options['BAUDRATE']
        to = self.options['time_out']

        port = self.get_arduino_port()
        try:
            ser = serial.Serial(port, baudrate = bd, timeout = to)
        except:
            print("Error: Cannot create serial connection with Arduino.")

        self.ser_conn = ser

    def establish_temperature_thread_(self):
        sp = 1 / self.options['temp_refresh_rate']
        ep = self.options['epsilon_time']
        conn = self.ser_conn
        lock = self.ser_lock

        self.temperature_thread = GCTemperature( self, conn, lock, args = (sp, ep) )
        self.temperature_thread.start()
        self.temp_thread_running = True

    def establish_GC_(self):
        se = self.options['single_ended']
        self.gc = GC(se)
        self.gc_lock = self.gc.get_lock()

    def establish_options_(self, uo):
        self.options = {'frame_size':(1200,600), 'sash_size':400, 'data_samp_rate':5.0,
                        'time_out':3, 'epsilon_time':0.001, 'plot_refresh_rate':2.0, 'temp_refresh_rate':1.0,
                        'single_ended':True, 'indices':{'v':0,'a':1,'t':2,'dt':3}, 'area_accuracy': 8,
                        'units_str':{'x-axis':'Time [seconds]' , 'y-axis':'Detector Response [volts]'},
                        'gc_file_indices': {'cd':'Current Data', 'pd':'Previous Data', 'rn':'Run Number'},
                        'window':3}

        _constants = {'BODY_FONT_SIZE': 11, 'HEADER_FONT_SIZE':18,'EXTRA_SPACE':10, 'BORDER':10}
        self.options.update(_constants)
        self.options.update(uo)
        self.options['frame_size'] = self.options['DEFAULT_FRAME_SIZE']
        self.options['sash_size'] = self.options['DEFAULT_SASH_SIZE']


    '''
    Lock function
    '''
    def is_frame_data_locked(self):
        _il = self.curr_data_frame_lock.locked()
        return _il

    '''
    Frame data functions
    '''
    '''
        Setters
    '''
    def set_frame_from_session_(self, filename):
        cd , pd, rn = self.parse_session(filename)

        _l = self.curr_data_frame_lock
        with _l:
            self.set_curr_data_w_ref_(cd)

        _gcl = self.gc_lock
        with _gcl:
            self.gc.set_curr_data_w_ref_(cd)

        self.prev_data = pd
        self.run_number = rn

    def parse_session(self, name):
        # # Format of JSON .gc filetype
        # curr_session = {
        # 'Date' : date_str ,
        # 'Time' : time_str ,
        # 'Current Data' : curr_data ,
        #  'Previous Data': prev_data
        # }

        _djson = self.load_json_file(name)

        data_dict_numpy = self.reverse_jsonify(_djson)

        ind = self.options['gc_file_indices']

        _cd = ind['cd']
        _pd = ind['pd']
        _rn = ind['rn']

        cd = data_dict_numpy[_cd]

        pd = data_dict_numpy[_pd]

        rn = data_dict_numpy[_rn]

        return (cd , pd, rn)

    def load_json_file(self, n):
        with open(n, encoding ='utf-8') as json_file:
            _d = json.load(json_file)
        return _d

    '''
    dict(lists)->dict(numpys)
    '''
    def reverse_jsonify(self, json_dict):
        numpy_dict = json_dict
        ind = self.options['gc_file_indices']

        _cd = ind['cd']
        _curr_data = [val for key, val in numpy_dict[_cd].items()]
        numpy_dict.update({_cd : np.array(_curr_data)})

        _pd = ind['pd']
        _prev_data = []
        for data_slice in numpy_dict[_pd]:
             _arr = [val for key,val in data_slice.items() ]
             _np_arr = np.array(_arr)
             _prev_data.append(_np_arr)

        numpy_dict.update({_pd:_prev_data})

        return numpy_dict

    def update_curr_data_(self):
        _gcl = self.gc.get_lock()
        with _gcl:
            _d = self.gc.get_curr_data()

        _l = self.curr_data_frame_lock
        with _l:
            self.set_curr_data_(_d)

    def curr_to_prev_(self):
        _l = self.curr_data_frame_lock
        with _l:
            _d = self.get_curr_data_copy()

        self.prev_data.append(_d)
        self.re_int_curr_data()

    def prev_to_curr_(self):
        d = self.prev_data.pop()

        _l = self.curr_data_frame_lock
        with _l:
            self.set_curr_data_(d)

        self.run_number -= 1

    def re_int_curr_data(self):
        _dims = self.gc.get_dims()

        _l = self.curr_data_frame_lock
        with _l:
            _z = np.zeros((_dims, 0))
            self.set_curr_data_w_ref_(_z)

    def set_curr_data_(self, d):
        _il = self.is_frame_data_locked()
        if _il:
            d = np.copy(d)
            self.curr_data_frame = d

    def set_curr_data_w_ref_(self, d):
        _il = self.is_frame_data_locked()
        if _il:
            self.curr_data_frame = d

    '''
        Getters
    '''
    def get_curr_data(self):
        _il = self.is_frame_data_locked()
        if _il:
            _d = self.curr_data_frame

        return _d

    def get_curr_data_copy(self):
        _il = self.is_frame_data_locked()
        if _il:
            _d = self.curr_data_frame
            _c = np.copy(_d)

        return _c

    def get_prev_data_copy(self):
        _pd = self.prev_data
        _pdc = [ np.copy(_item) for _item in _pd ]
        return _pdc

    def get_figure(self):
        return self.panel_detector.get_figure()

    '''
    Button Events
    '''
    def on_temp_txt_ctrl(self, ov_str, inj_str):
        self.set_temp_ser_cmd(ov_str, inj_str)

    def set_temp_ser_cmd(self, ov_str_val, inj_str_val):
        base_str = self.options['SET_TMP_CMD_STR']
        ov_ind = self.options['OVEN_INDEX']
        inj_ind = self.options['INJ_INDEX']

        ov_str_val = ov_str_val[:3]
        while len(ov_str_val) < 3:
            ov_str_val = ' ' + ov_str_val

        inj_str_val = inj_str_val[:3]
        while len(inj_str_val) < 3:
            inj_str_val = ' ' + inj_str_val

        print("Setting oven temperature to: {:s}".format(ov_str_val))
        print("Setting injector temperature to: {:s}".format( inj_str_val))

        base_str = base_str[:4*ov_ind] + ov_str_val + base_str[4*(ov_ind + 1) -1:]
        base_str = base_str[:4*inj_ind] + inj_str_val + base_str[4*(inj_ind + 1) -1:]

        b_str = base_str.encode()

        ser = self.ser_conn
        lock = self.ser_lock
        with lock:
            ser.flushInput()
            ser.flushOutput()

        time.sleep(ser_delay)

        with lock:
            _ = ser.write(b_str)

    def on_play_btn(self):
        if self.data_paused:
            gc_thread.un_pause()
            self.data_paused = False
            return
        elif self.data_running:
            return

        rr = self.options['data_samp_rate']
        sp = 1 / rr
        ep = self.options['epsilon_time']

        self.data_running= True
        self.run_number += 1
        self.gc.inc_run_num_()

        self.curr_to_prev_()
        self.gc.curr_to_prev_()

        gcl = self.gc_lock
        self.gc_cond = threading.Condition(gcl)

        gc = self.gc
        condition = self.gc_cond
        _ind = self.options['indices']
        self.data_rover_thread = GCData(gc, condition, _ind, args = ( sp, ep ) )

        rsp = self.options['plot_refresh_rate']
        lock = self.curr_data_frame_lock
        self.receiver_thread = GCReceiver(self, lock, gc, condition, args = ( rsp, ep ))

        self.data_rover_thread.start()
        self.receiver_thread.start()

        self.plotter_thread = GCPlotter(self, args=(rsp,ep))
        self.plotter_thread.start()

    def on_paus_btn(self):
        gc_thread = self.data_rover_thread

        if not self.data_paused:
            gc_thread.pause()
            self.data_paused = True

    def on_stop_btn(self):
        if self.data_running:
            self.stop_data_coll_()

    def stop_data_coll_(self):
        self.plotter_thread.stop()
        self.plotter_thread.join()

        self.receiver_thread.stop()
        self.receiver_thread.join()

        self.data_rover_thread.stop()
        self.data_rover_thread.join()

        self.data_running = False

        if self.curr_data_frame_lock.locked():
            self.curr_data_frame_lock.release()

        print('Message: Stopped data collection threads.')

    def on_plot_btn(self):
        if self.data_running:
            self.stop_data_coll_()

        self.panel_detector.update_curr_data_()
        self.panel_detector.draw()

    def on_clr_btn(self):
        if self.data_running:
            self.stop_data_coll()

        if self.run_number > 0:
            with self.curr_data_frame_lock:
                self.update_curr_data_()
                self.prev_data.append(self.curr_data)

        _dims = self.gc.get_dims()
        with self.curr_data_frame_lock:
            self.curr_data = np.zeros((_dims,0))

    '''
    Formatting/building functions
    '''
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

    '''
    Menu events
    '''
    def on_quit(self , err):
        if self.data_running:
            self.stop_data_coll_()

        self.Close()

    def on_saveas(self, err):
        _saveas_gc_window = SaveasGC( self, self.options)

    def on_open(self, err):
        _open_window = OpenWindow(self, self.options)

    def on_png_save(self, err):
        _saveas_png_window = SaveasPNG(self, self.options)

    def on_jpg_save(self, err):
        _saveas_jpg_window = SaveasJPG(self, self.options)

    def on_previous_set(self, err):
        self.prev_to_curr_()

    def on_data_integrate(self, err):
        if not self.data_running:
            ans = self.gc.integrate_volt()
            print("The integral of voltage over the sampling period is: ")
            print(ans)
            self.gc.calc_cumsum_into_area_()
            self.update_curr_data_()

    def on_data_normalize(self, err):
        if not self.data_running:
            self.gc.normalize_volt_()
            self.update_curr_data_()

            self.panel_detector.update_curr_data_()
            self.panel_detector.draw()

    def on_clean_time(self, err):
        if not self.data_running:
            self.gc.clean_time_()
            self.update_curr_data_()

            self.panel_detector.update_curr_data_()
            self.panel_detector.draw()

    def on_fill(self, err):
        if not self.data_running:
            self.panel_detector.fill_under_()

    def on_label_peaks(self, err):
        if not self.data_running:
            areas = self.gc.integrate_peaks()
            # list of (x,y) pairs
            maximas = self.gc.get_peak_local_maximas()

            self.panel_detector.update_curr_data_()
            self.panel_detector.label_peaks_(areas, maximas)

    def on_mov_mean(self, err):
        if not self.data_running:
            _w = self.options['window']
            self.gc.mov_mean_(_w)
            self.update_curr_data_()

            self.panel_detector.update_curr_data_()
            self.panel_detector.draw()

    '''
    Defaults overridden
    '''
    def __del__(self):
        pass

    def main(self):
        pass

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

# Popup Configuration Window
# Maybe wx.PopupWindow later?
class GCConfigPopup(wx.Frame):
    def __init__(self, parent, text, type, variable_in_focus):
        self.parent = parent
        self.options = self.parent.options

        self.prompt = text

        self.default = variable_in_focus
        self.type = type

        self.fonts = self.create_fonts()

        _p = parent
        _id = wx.ID_ANY
        _t = 'Configuration Popup Window'
        _pos = wx.DefaultPosition
        _s = (250, 100)
        _sty = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, _p, _id, _t, _pos, _s, _sty)

    def create_fonts(self):
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(self.options['BODY_FONT_SIZE'])
        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(self.options['HEADER_FONT_SIZE'])

        return {'font':font,'header_font':header_font}

    def create_frame_(self):
        hf = self.fonts['header_font']
        f = self.fonts['font']
        b = self.options['BORDER']

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        _t = self.prompt
        _s = (100,50)
        txt_prompt = wx.StaticText(self, label = _t, size= _s)

        txt_prompt.SetFont(hf)
        hbox.Add(txt_prompt, proportion=1)

        _dv = self.default
        _p = wx.DefaultPosition
        _s = (50,50)
        self.tc_val = wx.TextCtrl(self, value = _dv, pos = _p, size = _s)
        self.tc_val.SetFont(hf)

        hbox.Add(self.tc_val, proportion=1, border= b)

        _id = wx.ID_ANY
        _t = 'Enter'
        _s = (50, 50)
        self.btn_entr = wx.Button(self, id=_id, label=_t, size = _s)
        self.Bind(wx.EVT_BUTTON, self.entrbtn_click_evt, self.btn_entr)

        hbox.Add(self.btn_entr, proportion=1)

        self.SetSizer(hbox)
        self.Centre()
        self.Show()

    def entrbtn_click_evt(self, event):
        pass

#DirectoryWindow(s)
class DirectoryWindow(wx.Frame):
    def __init__(self, parent, ops):
        self.parent = parent
        self.cwd = os.getcwd()

        self.options = ops
        self.fonts = self.create_fonts()

        _p = parent
        _id = wx.ID_ANY
        _t = wx.EmptyString
        _pos = wx.DefaultPosition
        _s = (600, 600)
        _sty = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, _p, _id, _t, _pos, _s, _sty)

        self.create_frame_()
        self.update_cwd()

    def create_fonts(self):
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(self.options['BODY_FONT_SIZE'])
        header_font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        header_font.SetPointSize(self.options['HEADER_FONT_SIZE'])

        return {'font':font,'header_font':header_font}

    def create_frame_(self):
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

        global imdir
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
    def __init__(self, parent, ops):
        str = 'Save As'
        DirectoryWindow.__init__(self,parent, ops)
        self.SetTitle(str)
        self.btn_entr.SetLabel(str)

    def entrbtn_click_evt(self, event):
        pass

class SaveasGC(SaveasWindow):
    def __init__(self, parent, ops):
        SaveasWindow.__init__(self, parent, ops)

        self.SetTitle('Save Session As GC')
        self.btn_entr.SetLabel('Save as .gc')
        #Get important parameters
        self.parent = parent
        self.options = ops

    def entrbtn_click_evt(self, event):
        name = self.tc_name.GetValue()
        self.save_gc(name)

    def save_gc(self, name):
        _date = time.strftime('%d %m %Y (MM/DD/YYYY)', time.localtime())
        date_str = 'Current date: ' + _date + ' '
        _time = time.strftime('%H:%M:%S',time.localtime())
        time_str = 'Time at save: ' + _time

        _l = self.parent.curr_data_frame_lock
        with _l:
            data = self.parent.get_curr_data_copy()

        _ind = self.options['indices']
        _vi = _ind['v']
        _ai = _ind['a']
        _ti = _ind['t']
        _dti = _ind['dt']

        data_dict = {'v':data[_vi],'a':data[_ai],'t':data[_ti],'dt':data[_dti]}

        curr_data = self.jsonify_data(data_dict)

        prev_data = []

        list_data = self.parent.get_prev_data_copy()
        for data in list_data:
            data_dict = {'v':data[_vi],'a':data[_ai],'t':data[_ti],'dt':data[_dti]}
            _jsond  = self.jsonify_data(data_dict)
            prev_data.append(_jsond)

        if name[-3:] != '.gc':
            name = name + '.gc'

        run_num = self.parent.run_number

        # Format of JSON .gc filetype
        curr_session = {
        'Date' : date_str ,
        'Time' : time_str ,
        'Current Data' : curr_data ,
        'Run Number' : run_num,
         'Previous Data': prev_data
        }

        with codecs.open(name , 'w', encoding='utf-8') as json_file:
            json.dump(curr_session, json_file, separators =(',',':'),indent=4)

        self.Close()
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
    def __init__(self, parent, ops):
        SaveasWindow.__init__(self, parent, ops)

        self.SetTitle('Save Current Figure As PNG')
        self.btn_entr.SetLabel('Save as .png')
        self.figure = self.parent.get_figure()

    def entrbtn_click_evt(self, event):
        name = self.tc_name.GetValue()
        self.save_png(name)
        self.Close()

    def save_png(self, name):
        if name[-4:] == '.png':
            self.figure.savefig(name )
        else:
            self.figure.savefig(name + '.png')

class SaveasJPG(SaveasWindow):
    def __init__(self, parent, ops):
        SaveasWindow.__init__(self, parent, ops)

        self.SetTitle('Save Current Figure As JPEG')
        self.btn_entr.SetLabel('Save as .jpg')
        self.figure = self.parent.get_figure()

    def entrbtn_click_evt(self, event):
        name = self.tc_name.GetValue()
        self.save_jpg(name)
        self.Close()

    def save_jpg(self, name):
        if self.is_jpg(name):
            self.figure.savefig(name)
        else:
            self.figure.savefig(name + '.jpg')

    def is_jpg(self, n):
        if n[-4:] == '.jpg':
            return True
        return False

class OpenWindow(DirectoryWindow):
    def __init__(self, parent, ops):
        str = 'Open GC File'
        super().__init__( parent, ops)
        self.SetTitle(str)
        self.btn_entr.SetLabel('Open as .gc')

    def spec_cwdlist_dclick_evt(self,  choice, filename, extension):
        name = self.tc_name.GetValue()
        if self.is_gc(name):
            self.open_gc(name)
            self.Close()

    def open_gc(self, name):
        self.parent.set_frame_from_session_(name)

    def is_gc(self, name):
        if name[-3:] == '.gc':
            return True
        return False

# Threads
class GCTemperature(Thread):
    def __init__(self, frame, serial_connection, serial_lock, *args, **kwargs):
        super(GCTemperature, self).__init__()

        self.frame = frame

        self.sp = kwargs['args'][0] #sampling_period
        self.ep = kwargs['args'][1] #epsilon

        self._stop_event = threading.Event()

        self.ser_conn = serial_connection
        self.ser_lock = serial_lock

        self.oven_temp = None
        self.last_oven_temp = None
        self.oven_val_change = True
        self.oven_stc_txt = self.frame.panel_config.str_ov_fdbk_val

        self.inj_temp = None
        self.last_inj_temp = None
        self.oven_val_change = True
        self.inj_stc_txt = self.frame.panel_config.str_inj_fdbk_val

        self.last_update_time_raw = None

        self.ov_location = self.frame.options['OVEN_INDEX']
        self.inj_location = self.frame.options['INJ_INDEX']


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        sampling_period = self.sp
        epsilon = self.ep

        o_l = self.ov_location
        d_l = self.inj_location

        t_last = time.time()

        while not self.stopped():
            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.1)
                t_curr = time.time()

            t_last = t_curr

            bit_response = self.query_temp()

            temperatures = self.parse_response(bit_response)

            self.last_oven_temp = self.oven_temp
            self.last_inj_temp = self.inj_temp

            self.oven_temp = float(temperatures[0])
            self.inj_temp = float(temperatures[1])

            if self.last_oven_temp == self.oven_temp:
                self.oven_val_change = False
            else:
                self.oven_val_change = True

            if self.last_inj_temp == self.inj_temp:
                self.inj_val_change = False
            else:
                self.inj_val_change = True

            self.last_update_time_raw = time.time()

            if self.inj_val_change and self.oven_val_change:
                func = self.set_both_txt_ctrls
                args = temperatures
                wx.CallAfter(func, args)

            elif self.oven_val_change:
                ov_str = temperatures[0]

                func = self.oven_stc_txt.SetLabel
                args = ov_str

                wx.CallAfter(func, args)

            elif self.inj_val_change:
                inj_str = temperatures[1]

                func = self.inj_stc_txt.SetLabel
                args = inj_str
                wx.CallAfter(func, args)

    def query_temp(self):
        ser_delay = self.frame.options['SER_DELAY']
        # From c library. Defined in c_constants.py
        #READ_TMP_CMD_STR = '000 000 000 000'
        _str = self.frame.options['READ_TMP_CMD_STR']
        b_str = _str.encode()

        ser = self.ser_conn

        lock = self.ser_lock
        with lock:
            ser.flushInput()
            ser.flushOutput()

        time.sleep(ser_delay)

        with lock:
            _ = ser.write(b_str)
            while ser.in_waiting == 0:
                time.sleep(ser_delay)

        bit_response = []
        with lock:
            while ser.in_waiting > 0:
                line = ser.readline()
                bit_response.append(line)

        return bit_response


    def parse_response(self, resp):
        o_l = self.ov_location
        i_l = self.inj_location

        str_resp = [item.decode() for item in resp]
        str_resp = [item.strip('\r\n') for item in str_resp]

        ov_tmp = str_resp[o_l]

        inj_tmp = str_resp[i_l]

        temps = [ov_tmp, inj_tmp]

        return temps

    def set_both_txt_ctrls(self, temps):
        ov_str = temps[0]
        inj_str = temps[1]
        self.oven_stc_txt.SetLabel(ov_str)
        self.inj_stc_txt.SetLabel(inj_str)

class GCPlotter(Thread):
    def __init__(self, frame, *args, **kwargs):
        super(GCPlotter, self).__init__()

        self.frame = frame
        #self.curr_data_lock = lock

        self.sp = kwargs['args'][0]
        self.ep = kwargs['args'][1]

        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        sampling_period = self.sp
        epsilon = self.ep

        t_last = time.time()
        while not self.stopped():
            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.1)
                t_curr = time.time()

            t_last = t_curr

            self.frame.panel_detector.update_curr_data_()
            func = self.frame.panel_detector.draw
            wx.CallAfter(func)

class GCReceiver(Thread):
    def __init__(self, frame, lock, gc, condition, *args, **kwargs):
        super(GCReceiver, self).__init__()

        self.sp = kwargs['args'][0]
        self.ep = kwargs['args'][1]
        self.time_out = 1

        self._stop_event = threading.Event()

        self.frame = frame
        self.gc = gc
        self.data_lock = lock

        self.gc_cond = condition

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        sampling_period = self.sp
        epsilon = self.ep
        to = self.time_out

        t_last = time.time()
        while not self.stopped():
            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.01)
                t_curr = time.time()

            t_last = t_curr
            with self.gc_cond:
                val = self.gc_cond.wait(to)

            if val:
                with self.gc_cond:
                    gc_d = self.gc.get_curr_data()
                with self.data_lock:
                    self.frame.set_curr_data_(gc_d)

            else:
              print("Error: Timeout on data reception reached.")

class GCData(Thread):
    def __init__(self, gc, condition, indices, *args, **kwargs):
        super(GCData, self).__init__()

        self.sp = kwargs['args'][0]
        self.ep = kwargs['args'][1]
        self.indices = indices
        self.gc = gc
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        self.condition = condition
        #
        self.avail = False

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def pause(self):
        self._pause_event.set()

    def un_pause(self):
        self._pause_event.clear()

    def paused(self):
        return self._pause_event.is_set()

    def is_avail(self):
        return self.avail

    def run(self):
        t_last = time.time()

        sampling_period = self.sp
        epsilon = self.ep
        dims = self.gc.get_dims()

        while not self.stopped():
            while self.paused():
                time.sleep(.01)
                if self.stopped():
                    return

            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.01)
                t_curr = time.time()

            v = self.gc.measure_voltage()

            dt = t_curr - t_last
            t = t_curr
            t_last = t_curr

            new = np.zeros((dims, 1))

            ind = self.indices
            _vi = ind['v']
            _dti = ind['dt']
            _ti = ind['t']

            new[_vi] = v
            new[_dti] = dt
            new[_ti] = t
            # a default zero

            with self.condition:
                old = self.gc.get_curr_data()

            new = np.append(old, new, axis=1)

            with self.condition:
                self.gc.set_curr_data_(new)
                self.condition.notify_all()

#Panels
class DetectorPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL)

        self.parent = parent
        self.gcframe = parent.parent
        self.options = self.parent.options
        self.indices = self.options['indices']
        self.units_str = self.options['units_str']

        self.fonts = parent.create_fonts()

        self.create_panel()

    def create_panel(self):
        f = self.fonts['font']
        hf = self.fonts['header_font']
        b = self.options['BORDER']
        es = self.options['EXTRA_SPACE']
        bfs = self.options['BODY_FONT_SIZE']

        vbox = wx.BoxSizer(wx.VERTICAL)

        str_det_panel = wx.StaticText(self, label = 'Detector')
        str_det_panel.SetFont(hf)

        vbox.Add(str_det_panel, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border = b)
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

        self.Bind(wx.EVT_BUTTON, self.plot_btn_evt,self.btn_plot)

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

    def create_figure_(self):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        _xstr = self.units_str['x-axis']
        _ystr = self.units_str['y-axis']
        self.axes.set_xlabel(_xstr)
        self.axes.set_ylabel(_ystr)

        self.canvas = FigureCanvas(self, -1, self.figure)

    def create_control_box(self):
        b = self.options['BORDER']
        es = self.options['EXTRA_SPACE']

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.Bitmap(imdir + '/play_btn_20p.png',wx.BITMAP_TYPE_ANY)
        self.btn_ply = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))
        self.Bind(wx.EVT_BUTTON, self.ply_btn_evt, self.btn_ply)

        bmp = wx.Bitmap(imdir + '/paus_btn_20p.png',wx.BITMAP_TYPE_ANY)
        self.btn_paus = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))
        self.Bind(wx.EVT_BUTTON, self.paus_btn_evt, self.btn_paus)

        bmp = wx.Bitmap(imdir + '/stop_btn_20p.png',wx.BITMAP_TYPE_ANY)
        self.btn_stp = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size = (50,50))
        self.Bind(wx.EVT_BUTTON, self.stp_btn_evt, self.btn_stp)

        hbox.Add(self.btn_ply, border = b)
        hbox.Add((es,-1))
        hbox.Add(self.btn_paus, border =b)
        hbox.Add((es,-1))
        hbox.Add(self.btn_stp, border =b)
        hbox.Add((es,-1))

        return hbox

    def label_peaks_(self, areas, maximas):
        num_pts = len(areas)

        cd = self.get_curr_data()
        ind = self.gcframe.options['indices']
        _vi = ind['v']
        _ti = ind['t']

        v = cd[_vi]
        t = cd[_ti]

        accuracy = self.options['area_accuracy']

        for i in range(0,num_pts):
            _astr = str(areas[i])
            _text = 'Relative area:\n' + _astr[:accuracy]
            max_index , max_val  = maximas[i]
            _x = t[max_index]
            _y = v[max_index]
            self.axes.annotate(_text, xy= (_x,_y), xytext=(20,-20), xycoords='data', textcoords = 'offset pixels')

        _xstr = self.units_str['x-axis']
        _ystr = self.units_str['y-axis']
        self.axes.set_xlabel(_xstr)
        self.axes.set_ylabel(_ystr)

        func = self.canvas.draw
        wx.CallAfter(func)

    def fill_under_(self):
        cd = self.get_curr_data()
        _vi = self.indices['v']
        _ti = self.indices['t']
        v = cd[_vi]
        t = cd[_ti]
        self.axes.fill_between(t,v)
        func = self.canvas.draw
        wx.CallAfter(func)

    def draw(self):
        _vi = self.indices['v']
        _ti = self.indices['t']

        if self.curr_data.size != 0:
            self.axes.cla()
            self.axes.plot(self.curr_data[_ti], self.curr_data[_vi])

            _xstr = self.units_str['x-axis']
            _ystr = self.units_str['y-axis']
            self.axes.set_xlabel(_xstr)
            self.axes.set_ylabel(_ystr)

            func = self.canvas.draw
            wx.CallAfter(func)
        else:
            print("Error: Empty curr_data")

    def ply_btn_evt(self, event):
        self.gcframe.on_play_btn()

    def paus_btn_evt(self, event):
        self.gcframe.on_paus_btn()

    def stp_btn_evt(self, event):
        self.gcframe.on_stop_btn()

    def plot_btn_evt(self, event):
        self.gcframe.on_plot_btn()

    def update_curr_data_(self):
        with self.gcframe.curr_data_frame_lock:
            self.curr_data = self.gcframe.get_curr_data_copy()

    def clear_plot_btn_evt(self, event):
        self.gcframe.on_clr_btn()
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
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )

        self.parent = parent
        self.gcframe = parent.parent
        self.options = self.parent.options

        self.fonts = parent.create_fonts()

        self.create_panel()

    def create_panel(self):
        f = self.fonts['font']
        hf = self.fonts['header_font']
        b = self.options['BORDER']
        es = self.options['EXTRA_SPACE']
        bfs = self.options['BODY_FONT_SIZE']

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Temperature header
        self.build_static_header_()

        #Oven temp
        hbox_ov_set = self.build_oven_static_text_one()

        self.tc_ov_set = wx.TextCtrl(self)
        hbox_ov_set.Add(self.tc_ov_set, proportion=1)
        self.Bind(wx.EVT_TEXT , self.oven_set , self.tc_ov_set)

        self.vbox.Add(hbox_ov_set, flag=wx.LEFT|wx.TOP,border =b)

        hbox_ov_fdbk = self.build_oven_static_text_two()

        self.str_ov_fdbk_val = wx.StaticText(self, label = 'N/A')
        self.str_ov_fdbk_val.SetFont(f)
        hbox_ov_fdbk.Add(self.str_ov_fdbk_val)

        self.vbox.Add(hbox_ov_fdbk, flag=wx.LEFT|wx.TOP,border =b)

        self.vbox.Add((-1,es))

        #injector temp
        hbox_inj_set = self.build_inj_static_text_one()

        self.tc_inj_set = wx.TextCtrl(self)
        hbox_inj_set.Add(self.tc_inj_set, proportion = 1)
        self.Bind(wx.EVT_TEXT, self.inj_set , self.tc_inj_set)

        self.vbox.Add(hbox_inj_set, flag=wx.LEFT|wx.TOP,border =b)

        hbox_inj_fdbk = self.build_inj_static_text_two()

        self.str_inj_fdbk_val = wx.StaticText(self, label = 'N/A')
        self.str_inj_fdbk_val.SetFont(f)
        hbox_inj_fdbk.Add(self.str_inj_fdbk_val)

        self.vbox.Add(hbox_inj_fdbk, flag=wx.LEFT|wx.TOP,border =b)

        self.SetSizer(self.vbox)


    def oven_set(self, event):
        ov_str = self.tc_ov_set.GetLineText(1)
        inj_str = self.tc_inj_set.GetLineText(1)
        if len(ov_str) != 0 and len(inj_str != 0):
            self.gcframe.on_temp_txt_ctrl(ov_str, inj_str)

    def inj_set(self, event):
        ov_str = self.tc_ov_set.GetLineText(1)
        inj_str = self.tc_inj_set.GetLineText(1)
        if len(ov_str) != 0 and len(inj_str != 0):
            self.gcframe.on_temp_txt_ctrl(ov_str, inj_str)

    def build_inj_static_text_two(self):
        hbox_inj_fdbk = wx.BoxSizer(wx.HORIZONTAL)
        str_inj_fdbk = wx.StaticText(self, label = 'Injector Temp. Reading: ')
        f = self.fonts['font']
        str_inj_fdbk.SetFont(f)
        hbox_inj_fdbk.Add(str_inj_fdbk)

        return hbox_inj_fdbk

    def build_inj_static_text_one(self):
        hbox_inj_set = wx.BoxSizer(wx.HORIZONTAL)
        str_inj_set = wx.StaticText(self, label = 'Set Injector Temp.: ')
        f = self.fonts['font']
        str_inj_set.SetFont(f)
        hbox_inj_set.Add(str_inj_set)

        return hbox_inj_set

    def build_oven_static_text_one(self):
        hbox_ov_set = wx.BoxSizer(wx.HORIZONTAL)
        str_ov_set = wx.StaticText(self,label='Set Oven Temp.: ')
        f = self.fonts['font']
        str_ov_set.SetFont(f)
        hbox_ov_set.Add(str_ov_set)

        return hbox_ov_set

    def build_oven_static_text_two(self):
        hbox_ov_fdbk = wx.BoxSizer(wx.HORIZONTAL)
        str_ov_fdbk = wx.StaticText(self, label = 'Oven Temp. Reading: ')
        f = self.fonts['font']
        str_ov_fdbk.SetFont(f)
        hbox_ov_fdbk.Add(str_ov_fdbk)

        return hbox_ov_fdbk

    def build_static_header_(self):
        #Temperature
        str_temp = wx.StaticText(self, label = 'Temperature')
        hf = self.fonts['header_font']
        str_temp.SetFont(hf)
        b = self.options['BORDER']
        self.vbox.Add(str_temp, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,border =b)

        es = self.options['EXTRA_SPACE']
        self.vbox.Add((-1,es))

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

        # grapher_menu.Append(wx.ID_ANY, '&Edit Axes')
        #
        # grapher_menu.AppendSeparator()

        grapher_menu.Append(wx.ID_ANY, '&Save Image')

        graph_menu_saveim = wx.Menu()
        _png_save = graph_menu_saveim.Append(wx.ID_ANY, '&.png')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_png_save, _png_save)

        _jpg_save = graph_menu_saveim.Append(wx.ID_ANY,'&.jpg')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_jpg_save, _jpg_save)

        grapher_menu.Append(wx.ID_ANY, '&Save Image As...', graph_menu_saveim)

        _fill = grapher_menu.Append(wx.ID_ANY, '&Fill')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_fill, _fill)

        _label_peaks = grapher_menu.Append(wx.ID_ANY, '&Label Peaks')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_label_peaks, _label_peaks)

        return grapher_menu

    def create_data_menu(self):
        data_menu = wx.Menu()

        prev_set = data_menu.Append(wx.ID_ANY, '&Previous Set')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_previous_set, prev_set)

        data_menu_ops = wx.Menu()
        integ = data_menu_ops.Append(wx.ID_ANY, '&Integrate')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_data_integrate, integ )

        norm = data_menu_ops.Append(wx.ID_ANY, '&Normalize')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_data_normalize, norm)

        clean_time = data_menu_ops.Append(wx.ID_ANY, '&Clean Time Axis')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_clean_time, clean_time)

        lpf = data_menu_ops.Append(wx.ID_ANY, '&Apply Low Pass Filter')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_mov_mean, lpf)

        data_menu.Append(wx.ID_ANY, '&Operations...', data_menu_ops)

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

        item_quit = file_menu.Append(wx.ID_EXIT, '&Quit' , 'Quit application')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_quit,item_quit)

        return file_menu

if __name__ == '__main__':
    pass
