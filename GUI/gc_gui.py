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

from windows import GCSplitter, SaveasGC, SaveasPNG, SaveasJPG, OpenWindow

imdir = 'images'

# c serial cmd definition
READ_TMP_CMD_STR = '000 000 000 000'

# __future__!! better set it later
SET_TMP_CMD_STR = '000 000 000 000'

SER_DELAY = .01 #sec


# Frames
class GCFrame(wx.Frame):
    # self is MainApp(GCFrame)
    # parent is None
    def __init__(self, parent, user_options):
        self.set_options_(user_options)
        self.parent = parent

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = self.options['DEFAULT_FRAME_SIZE'], style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
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

        self.curr_data_frame = np.zeros((self.gc.dims, 0))
        self.update_curr_data_()

        self.prev_data = []
        self.run_number = 0

        self.data_running = False

    '''
    Building functions
    '''
    def get_arduino_port(self):
        possible = [x for x in os.listdir('/dev/') if 'ACM' in x]

        if len(possible) == 0:
            print("Error: No ACM ports found to connect to Arduino.")
            print("Continuing for now.")
            possible[0] = 'ttyACM0'
        elif len(possible) != 1:
            print("Error: Multiple possible ACM ports to connect Arduino")
            print("Defaulting to '/dev/ttyACM0'")
            possible[0] = 'ttyACM0'

        local = possible[0]
        string = '/dev/' + possible[0]

        return string

    def establish_serial_conn_(self):
        bd = self.options['baud_rate']
        to = self.options['time_out']

        port = self.get_arduino_port()
        try:
            ser = serial.Serial(port, baudrate = bd, timeout = to)
        except:
            print("Error connecting to serial...")

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
        self.gc_lock = self.gc.curr_data_lock

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
    def update_curr_data_(self):
        _gcl = self.gc.curr_data_lock
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

    def re_int_curr_data(self):
        _dims = self.gc.dims

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

    def set_options_(self, uo):
        self.constants = {'BODY_FONT_SIZE': 11, 'HEADER_FONT_SIZE':18,'EXTRA_SPACE':10, 'BORDER':10}
        self.options = {'frame_size':(800,400), 'sash_size':300, 'data_samp_rate':5.0, 'baud_rate':115200,
                        'time_out':3, 'epsilon_time':0.001, 'plot_refresh_rate':2.0, 'temp_refresh_rate':1.0,
                        'single_ended':True, 'indices':{'v':0,'area':1,'dt':2,'t':3}}
        self.options.update(self.constants)

        self.options.update(uo)

#BIG TODO
    def set_temp_ser_cmd(self, temp, which = 'oven'):
        if which == 'oven':
            pass
            # do something
            # SET_TMP_CMD_STR
        elif which == 'det':
            pass
            #
        else:
            print('Err')

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
        _pdc = np.copy(_pd)
        return _pdc

    def get_figure(self):
        return self.panel_detector.get_figure()

    '''
    Button Events
    '''
    def on_ov_txt_ctrl(self, string):
        print("Text control changed")
        print(string + " received")
        val = float(string)
        str = 'oven'

        with self.ser_lock:
            self.ser_cmd_set_temp(val, str)

    def on_det_txt_ctrl(self, string):
        val = float(string)
        str = 'det'

        with self.ser_lock:
            self.ser_cmd_set_temp(val, str)

    def on_play_btn(self):
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
        self.data_rover_thread = GCData(gc, condition, args = ( sp, ep ) )

        rsp = self.options['plot_refresh_rate']
        lock = self.curr_data_frame_lock
        self.receiver_thread = GCReceiver(self, lock, gc, condition, args = ( rsp, ep ))

        self.data_rover_thread.start()
        self.receiver_thread.start()

        self.plotter_thread = GCPlotter(self, args=(rsp,ep))
        self.plotter_thread.start()

    def on_stop_btn(self):
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

        print(self.curr_data_frame_lock.locked())
        print(self.gc.is_locked())

    def on_plot_btn(self):
        if self.data_running:
            self.stop_data_coll_()

        print('plot')
        self.panel_detector.update_curr_data_()
        self.panel_detector.draw()

    def on_clr_btn(self):
        if self.data_running:
            self.stop_data_coll()

        if self.run_number > 0:
            with self.curr_data_frame_lock:
                self.update_curr_data_()
                self.prev_data.append(self.curr_data)

        with self.curr_data_frame_lock:
            self.curr_data = np.zeros((self.gc.dims,0))

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

    def on_data_integrate(self, err):
        print("on integrate")
        print(self.data_running)
        if not self.data_running:
            ans = self.gc.integrate_volt()
            print("The integral is: ")
            print(ans)
            self.gc.calc_cumsum_into_area_()
            self.update_curr_data_()
        print('out integrate')

    def on_data_normalize(self, err):
        print("on normalize")
        print(self.data_running)
        _l = self.curr_data_frame_lock
        with _l:
            d = self.get_curr_data_copy()
        _inds = self.options['indices']
        _ti = _inds['t']
        t_first = d[_ti][0:10]
        print(t_first)
        if not self.data_running:
            self.gc.normalize_volt_()
            self.update_curr_data_()

            self.panel_detector.update_curr_data_()
            self.panel_detector.draw()
        print('out normalize')

    def on_clean_time(self, err):
        if not self.data_running:
            self.gc.clean_time_()
            self.update_curr_data_()

            self.panel_detector.update_curr_data_()
            self.panel_detector.draw()

    def on_fill(self, err):
        print("on fill")
        self.panel_detector.fill_under_()
        print('out fill')

    '''
    Defaults overridden
    '''
    def __del__(self):
        pass

    def main(self):
        pass

# Threads
class GCTemperature(Thread):
    def __init__(self, frame, serial_connection, serial_lock, *args, **kwargs):
        super(GCTemperature, self).__init__()

        self.frame = frame

        self.sp = kwargs['args'][0] #sampling_period
        self.ep = kwargs['args'][1] #epsilon

        self._stop_event = threading.Event()

        self.ser_conn = serial_connection
        print(self.ser_conn)
        self.ser_lock = serial_lock

        self.oven_temp = None
        self.last_oven_temp = None
        self.oven_val_change = True
        self.oven_stc_txt = self.frame.panel_config.str_ov_fdbk_val

        self.det_temp = None
        self.last_det_temp = None
        self.oven_val_change = True
        self.det_stc_txt = self.frame.panel_config.str_det_fdbk_val

        self.last_update_time_raw = None

        self.ov_location = 1
        self.det_location = 3


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        sampling_period = self.sp
        epsilon = self.ep

        o_l = self.ov_location
        d_l = self.det_location

        t_last = time.time()

        while not self.stopped():
            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.1)
                t_curr = time.time()

            t_last = t_curr

            with self.frame.ser_lock:
                bit_response = self.query_temp()

            temperatures = self.parse_response(bit_response)

            self.last_oven_temp = self.oven_temp
            self.last_det_temp = self.det_temp

            self.oven_temp = float(temperatures[0])
            self.det_temp = float(temperatures[1])

            if self.last_oven_temp == self.oven_temp:
                self.oven_val_change = False
            else:
                self.oven_val_change = True

            if self.last_det_temp == self.det_temp:
                self.det_val_change = False
            else:
                self.det_val_change = True

            self.last_update_time_raw = time.time()

            if self.det_val_change and self.oven_val_change:
                func = self.set_both_txt_ctrls
                args = temperatures
                wx.CallAfter(func, args)

            elif self.oven_val_change:
                ov_str = temperatures[0]

                func = self.oven_stc_txt.SetLabel
                args = ov_str

                wx.CallAfter(func, args)

            elif self.det_val_change:
                det_str = temperatures[1]

                func = self.det_stc_txt.SetLabel
                args = det_str
                wx.CallAfter(func, args)



    def query_temp(self):
        # From c library. Defined in c_constants.py
        #READ_TMP_CMD_STR = '000 000 000 000'
        b_str = READ_TMP_CMD_STR.encode()


        ser = self.ser_conn

        ser.flushInput()
        ser.flushOutput()

        time.sleep(.025)

        _ = ser.write(b_str)
        while ser.in_waiting == 0:
            time.sleep(SER_DELAY)

        bit_response = []
        while ser.in_waiting > 0:
            line = ser.readline()
            bit_response.append(line)
        return bit_response


    def parse_response(self, resp):
        o_l = self.ov_location
        d_l = self.det_location

        str_resp = [item.decode() for item in resp]
        str_resp = [item.strip('\r\n') for item in str_resp]

        ov_tmp = str_resp[o_l]

        det_tmp = str_resp[d_l]

        temps = [ov_tmp, det_tmp]

        return temps

    def set_both_txt_ctrls(self, temps):
        ov_str = temps[0]
        det_str = temps[1]
        self.oven_stc_txt.SetLabel(ov_str)
        self.det_stc_txt.SetLabel(det_str)

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
                print("notification received about item production...")

                with self.gc_cond:
                    gc_d = self.gc.get_curr_data()
                with self.data_lock:
                    self.frame.set_curr_data_(gc_d)

            else:
              print("waiting timeout...")

class GCData(Thread):
    def __init__(self, gc, condition, *args, **kwargs):
        super(GCData, self).__init__()

        self.sp = kwargs['args'][0]
        self.ep = kwargs['args'][1]
        self.gc = gc
        self._stop_event = threading.Event()

        self.condition = condition
        #
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
        dims = self.gc.dims

        while not self.stopped():
            t_curr= time.time()
            while (t_curr - epsilon -t_last < sampling_period):
                time.sleep(.01)
                t_curr = time.time()

            v = self.gc.measure_voltage()

            dt = t_curr - t_last
            t = t_curr
            t_last = t_curr

            new = np.zeros((dims, 1))

            indices = self.gc.indices
            _vi = indices['v']
            _dti = indices['dt']
            _ti = indices['t']

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
            print('new daata')

        print('done running')

#Panels
class DetectorPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL)

        self.parent = parent
        self.gcframe = parent.parent
        self.options = self.parent.options
        self.indices = self.options['indices']

        self.fonts = parent.create_fonts()

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

    def fill_under_(self):
        cd = self.get_curr_data()
        _vi = self.indices['v']
        _ti = self.indices['t']
        v = cd[_vi]
        t = cd[_ti]
        self.axes.fill_between(t,v)

    def draw(self):
        _vi = self.indices['v']
        _ti = self.indices['t']

        if self.curr_data.size != 0:
            self.axes.cla()
            self.axes.plot(self.curr_data[_ti], self.curr_data[_vi])
            func = self.canvas.draw
            wx.CallAfter(func)

    def ply_btn_evt(self, event):
        self.gcframe.on_play_btn()

    def stp_btn_evt(self, event):
        self.gcframe.on_stop_btn()

    def plot_btn_evt(self, event):
        self.gcframe.on_plot_btn()

    def update_curr_data_(self):
        with self.gcframe.curr_data_frame_lock:
            self.curr_data = self.gcframe.get_curr_data_copy()

        if self.curr_data.size != 0:
            init_time = self.curr_data[2][0]
            self.curr_data[2] = self.curr_data[2] - init_time

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
        self.Bind(wx.EVT_TEXT_ENTER, self.oven_set , self.tc_ov_set)

        self.vbox.Add(hbox_ov_set, flag=wx.LEFT|wx.TOP,border =b)

        hbox_ov_fdbk = self.build_oven_static_text_two()

        self.str_ov_fdbk_val = wx.StaticText(self, label = 'N/A')
        self.str_ov_fdbk_val.SetFont(f)
        hbox_ov_fdbk.Add(self.str_ov_fdbk_val)

        self.vbox.Add(hbox_ov_fdbk, flag=wx.LEFT|wx.TOP,border =b)

        self.vbox.Add((-1,es))

        #Detector temp
        hbox_det_set = self.build_det_static_text_one()

        self.tc_det_set = wx.TextCtrl(self)
        hbox_det_set.Add(self.tc_det_set, proportion = 1)
        self.Bind(wx.EVT_TEXT_ENTER, self.det_set , self.tc_det_set)

        self.vbox.Add(hbox_det_set, flag=wx.LEFT|wx.TOP,border =b)

        hbox_det_fdbk = self.build_det_static_text_two()

        self.str_det_fdbk_val = wx.StaticText(self, label = 'N/A')
        self.str_det_fdbk_val.SetFont(f)
        hbox_det_fdbk.Add(self.str_det_fdbk_val)

        self.vbox.Add(hbox_det_fdbk, flag=wx.LEFT|wx.TOP,border =b)

        self.SetSizer(self.vbox)


    def oven_set(self, event):
        str = self.tc_ov_set.GetLineText()
        self.gcframe.on_ov_txt_ctrl(str)

    def det_set(self, event):
        str = self.tc_det_set.GetLineText()
        self.gcframe.on_det_txt_ctrl(str)

    def build_det_static_text_two(self):
        hbox_det_fdbk = wx.BoxSizer(wx.HORIZONTAL)
        str_det_fdbk = wx.StaticText(self, label = 'Detector Temp. Reading: ')
        f = self.fonts['font']
        str_det_fdbk.SetFont(f)
        hbox_det_fdbk.Add(str_det_fdbk)

        return hbox_det_fdbk

    def build_det_static_text_one(self):
        hbox_det_set = wx.BoxSizer(wx.HORIZONTAL)
        str_det_set = wx.StaticText(self, label = 'Set Detector Temp.: ')
        f = self.fonts['font']
        str_det_set.SetFont(f)
        hbox_det_set.Add(str_det_set)

        return hbox_det_set

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

        grapher_menu.Append(wx.ID_ANY, '&Edit Axes')

        grapher_menu.AppendSeparator()

        grapher_menu.Append(wx.ID_ANY, '&Save Image')

        graph_menu_saveim = wx.Menu()
        _png_save = graph_menu_saveim.Append(wx.ID_ANY, '&.png')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_png_save, _png_save)

        _jpg_save = graph_menu_saveim.Append(wx.ID_ANY,'&.jpg')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_jpg_save, _jpg_save)

        grapher_menu.Append(wx.ID_ANY, '&Save Image As...', graph_menu_saveim)

        _fill = grapher_menu.Append(wx.ID_ANY, '&Fill')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_fill, _fill)

        return grapher_menu

    def create_data_menu(self):
        data_menu = wx.Menu()

        data_menu.Append(wx.ID_ANY, '&Previous Set')
        data_menu_ops = wx.Menu()
        integ = data_menu_ops.Append(wx.ID_ANY, '&Integrate')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_data_integrate, integ )

        norm = data_menu_ops.Append(wx.ID_ANY, '&Normalize')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_data_normalize, norm)

        clean_time = data_menu_ops.Append(wx.ID_ANY, '&Clean Time Axis')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_clean_time, clean_time)

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

        file_menu.Append(wx.ID_PRINT, '&Print')
        file_menu.AppendSeparator()

        item_quit = file_menu.Append(wx.ID_EXIT, '&Quit' , 'Quit application')
        self.parent.Bind(wx.EVT_MENU, self.parent.on_quit,item_quit)

        return file_menu

if __name__ == '__main__':
    pass
