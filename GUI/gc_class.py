'''
Name: gc_class.py
Authors: Conor Green and Matt McPartlan
Description: Mid-level abstraction that will do most of the work. User interaction as well as data processing.
Usage: Call as main
Copyright: Uses free library created by Adafruit and/or Carter Nelson at MIT. See code at: Adafruit [repo](https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/tree/master/adafruit_ads1x15)
        : Copyright is written in README of [ADS1x11.md](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/ADS1x15.md)
Version:
1.0 - 26 January 20 - Initial creation. Skeleton to outline work for later
1.1 - 18 February 20 - Initialized and created some methods for ADS1115 and numpy
1.2 - 20 February 20 - Added methods for data collection and organizing self variables
1.3 - 21 February 20 - Debugged and works in preliminary testing!

2.0 - 21 April 2020 - Final version. Sufficiently supports gc_gui.py in data collection with simple methods. ...
                        Old methods, that can plot, print, etc. are left at the end for future debugging/testing.
2.1 - 22 April 2020 - Integrate and normalize voltage methods.
2.2 - 22 April 2020 - Huge security upgrade. Moved lock to here (gc_class) and protected curr_data through getters and setters.
2.3 - 24 April 2020 - Modified lock structure. Added re_init_data and curr_to_prev to move current data to prev_data list.

3.0 - 24 April 2020 - Clean version that works great with gui script. Version 3 is very pydocs friendly and has accompanying html, gc_class.html
'''

# GPIO imports
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Extra
import time

# Numpy and Matplotlib
import numpy as np
import matplotlib.pyplot as plt

from threading import Lock

class GC:
    '''
    Modification functions: clean_time_, calc_cumsum_into_area_, normalize_volt_, mov_mean_, curr_to_prev_
    Math functions: integrate_volt, break_into_peaks
    helper functions: define_peaks, reint_curr_data, inc_run_num_, integrate
    ADS configuration functions: reint_ADS, set_gain, set_mode
    Lock functions: get_lock, is_locked
    Getters: get_curr_data, get_volt, get_time
    Setters: set_curr_data_, set_time_w_ref_, set_volt_, set_time_, set_time_w_ref_, set_area_
    Printer functions: print_voltage, print_value
    Measurement functions: measure_voltage, measure_value
    '''

    #@param: single_ended = True if single ended ADC and vice-versa
    def __init__(self, single_ended):
        self.__version__ = '3.0'
        self.__authors__ = 'Conor Green and Matt McPartlan'

        #ADS1115
        self.i2c = busio.I2C(board.SCL , board.SDA)
        self.ads = ADS.ADS1115(self.i2c)

        self.single_ended = single_ended # T/F
        self.port0 = ADS.P0 # Later allow user input
        self.port1 = ADS.P1

        if single_ended:
            self.chan = AnalogIn(self.ads , self.port0)
        else:
            self.chan = AnalogIn(self.ads, self.port0 , self.port1)

        #Numpy/data
        self.dims = 4 #voltage, dt, t
        self.indices = {'v':0,'a':1,'dt':2,'t':3}
        self.curr_data = np.zeros((self.dims, 0))
        self.curr_data_lock = Lock()
        self.time_out = 1 #sec
        self.epsilon = 0.01
        self.min_noise_after_norm = 0.2
        self.prev_data = []
        self.run_num = 0

    #@description: Subtracts initial time from all time points => t[0] = 0
    def clean_time_(self):
        if self.run_num > 0:
            to = self.time_out
            _e = self.curr_data_lock.acquire(to)
            t = self.get_time()
            _e = self.curr_data_lock.release()

            # Hokey fix in case
            if t[0] == 0:
                t[0] = t[1]-.01
                t = t - t[0]
            else:
                t = t - t[0]

            _e = self.curr_data_lock.acquire(to)
            self.set_time_(t)
            _e = self.curr_data_lock.release()

    #@description: Calculates the cumulative sum of the voltage at each point and stores the result in area.
    def calc_cumsum_into_area_(self):
        to = self.time_out
        #ignore err for now
        _e = self.curr_data_lock.acquire(to)
        voltage = self.get_volt()
        _e = self.curr_data_lock.release()

        cs = np.cumsum(voltage)

        _e = self.curr_data_lock.acquire(to)
        self.set_area_(cs)
        _e = self.curr_data_lock.release()

    #@description: Normalizes (integral[voltage] = 1 & min[voltage] = 0) the voltage in place.
    def normalize_volt_(self):
        to = self.time_out
        #ignore error for now
        _e = self.curr_data_lock.acquire(to)
        volt = self.get_volt()
        _e = self.curr_data_lock.release()

        print('acquired volt')

        _min = volt.min()
        volt = volt - _min

        _area = self.integrate_volt(volt)
        volt = volt / _area

        _e = self.curr_data_lock.acquire(to)
        self.set_volt_(volt)
        _e = self.curr_data_lock.release()

    #@description: Applies moving mean of window size given to voltage via convolution
    #@param: window size
    def mov_mean_(self, window):
        to = self.time_out
        _e = self.curr_data_lock.acquire(to)
        volt = self.get_volt()
        _e = self.curr_data_lock.release()

        np.convolve(vec, np.ones((window,))/window, mode='valid')

    #@description: Appends current data copy to previoius data list and sets current data back to zero vector.
    def curr_to_prev_(self):
        _l = self.curr_data_lock
        with _l:
            _d = self.get_curr_data()

        self.prev_data.append(_d)
        self.reint_curr_data()

    #@returns: int or float that is the area of voltage, including negatives
    def integrate_volt(self):
        to = self.time_out
        #ignore err for now
        _e = self.curr_data_lock.acquire(to)
        voltage = self.get_volt()
        _e = self.curr_data_lock.release()

        if len(voltage) != 0:
            _l = 0
            _h = -1
            _a = self.integrate(voltage, _l, _h)
            return _a
        else:
            print("No data")

    #@param: directly given voltage vector
    #@returns: int or float that is the area of voltage, including negatives
    def integrate_volt(self, voltage):
        print('direct called')
        if len(voltage) != 0:
            _l = 0
            _h = -1
            _a = self.integrate(voltage, _l, _h)
            print(_a)
            return _a
        else:
            print("No data")

    #@state: UNFINISHED
    #@description: Breaks the voltage vector into potential peaks. Simple and untested algorithm.
    #@returns: Indices of centers of peaks
    def break_into_peaks(self):
        pass
        ep = self.epsilon
        if abs(self.integrate_volt() -1.0 ) > ep:
            self.normalize_volt_()

    '''
    helper functions: define_peaks, reint_curr_data, inc_run_num_, integrate
    '''
    def define_peaks(self):
        to = self.time_out
        _e = self.curr_data_lock.acquire(to)
        volt = self.get_volt()
        _e = self.curr_data_lock.release()

        thresh = self.min_noise_after_norm
        large = False
        uphill = False

        window = 100

        deriv = np.diff(volt, order)

        for pt in volt:
            print(pt)

    def integrate(self, arr, low, high):
        if low < len(arr) -1:
            arr = arr[low]
            high = high - low

        tot_area = np.cumsum(arr)
        if high == -1:
            area = tot_area[-1]
        elif high < len(arr) -1:
            area = tot_area[high]
        else:
            print("High index in integration out of bounds")
            area = tot_area[-1]

        return area

    def reint_curr_data(self):
        _dims = self.dims

        _l = self.curr_data_lock
        with _l:
            _z = np.zeros((_dims, 0))
            self.set_curr_data_w_ref_(_z)

    def inc_run_num_(self):
        self.run_num += 1

    '''
    ADS configuration functions: reint_ADS, set_gain, set_mode
    '''
    def reinit_ADS(self):
        self.i2c = busio.I2C(board.SCL , board.SDA)
        self.ads = ADS.ADS1115(self.i2c)

        self.chan = AnalogIn(ads , self.port0) if self.single_ended else AnalogIn(ads, self.port0 , self.port1)

    def set_gain(self, g):
        self.ads.gain = g

    def set_mode(self, se):
        self.single_ended = se
        self.reinit_ADS()

    '''
    Lock functions: get_lock, is_locked
    '''
    def get_lock(self):
        return self.curr_data_lock

    def is_locked(self):
        _il = self.curr_data_lock.locked()
        return _il

    '''
    Getters: get_curr_data, get_volt, get_time
    '''
    def get_curr_data(self):
        _il = self.is_locked()
        if _il:
            _d = np.copy(self.curr_data)
            return _d
        else:
            print('get_curr_data: no access')

    def get_volt(self):
        is_locked = self.is_locked()
        _vi = self.indices['v']
        if is_locked:
            _v = np.copy(self.curr_data[_vi])
            return _v
        else:
            print('get_volt: no access')

    def get_time(self):
        _il = self.is_locked()
        _ti = self.indices['t']
        if _il:
            _t = self.curr_data[_ti]
            return _t
        else:
            print('get_time: no access')

    '''
    Setters: set_curr_data_, set_time_w_ref_, set_volt_, set_time_, set_time_w_ref_, set_area_
    '''
    def set_curr_data_(self, d):
        _il = self.is_locked()
        if _il:
            d = np.copy(d)
            self.curr_data = d
        else:
            print('set_curr_data: no access')

    def set_curr_data_w_ref_(self, d):
        _il = self.is_locked()
        if _il:
            self.curr_data = d
        else:
            print('set_curr_data_w_ref: no access')

    def set_volt_(self, d):
        is_locked = self.is_locked()
        _vi= self.indices['v']
        if is_locked:
            d = np.copy(d)
            self.curr_data[_vi] = d
        else:
            print('set_volt: no access')

    def set_time_(self, d):
        _il = self.is_locked()
        _ti = self.indices['t']
        if _il:
            d = np.copy(d)
            self.curr_data[_ti] = d
        else:
            print('set_time: no access')

    def set_time_w_ref_(self, d):
        _il = self.is_locked()
        _ti = self.indices['t']
        if _il:
            self.curr_data[_ti] = d
        else:
            print('set_time_w_ref: no access')

    def set_area_(self, d):
        _il = self.is_locked()
        _ai = self.indices['a']
        if _il:
            d = np.copy(d)
            self.curr_data[_ai] = d
        else:
            print('set_area_w_ref: no access')

    '''
    Printer functions: print_voltage, print_value
    '''
    def print_voltage(self):
        print(self.chan.voltage)

    def print_value(self):
        print(self.chan.value)

    '''
    Measurement functions: measure_voltage, measure_value
    '''
    def measure_voltage(self):
        return self.chan.voltage

    def measure_value(self):
        return self.chan.value

    '''
    Temporary/old methods
    '''
    # old, dont trust
    def graph_curr_data_on_popup(self):
        plt.figure()
        to = self.time_out
        _e = self.curr_data_lock.acquire(to)
        t = self.get_time()
        v = self.get_volt()
        _e = self.curr_data_lock.release(to)
        plt.scatter( t, v )
        plt.show()

    # old, dont trust
    def coll_volt_const_pts(self , num_pts):
        _vi = self.indices['v']
        _ai = self.indices['a']
        _dti = self.indices['dt']
        _ti = self.indices['i']

        temp_data_arr =  np.zeros((self.dims , num_pts ) )

        t_start = time.time()
        for i in range(0,num_pts):
            time.sleep(.01)
            temp_data_arr[_vi][i] = self.measure_voltage()
            temp_data_arr[_ai] = None
            t_curr = time.time()
            temp_data_arr[_dti][i] = t_curr - t_start
            temp_data_arr[_ti][i] = t_curr

        return voltage_an_dtime

    # old, dont trust
    def coll_volt_const_pts_self(self, num_pts):
        self.run_num += 1
        self.prev_data.append(self.curr_data)
        self.curr_data = self.coll_volt_const_pts(num_pts)
        print(self.curr_data)

if __name__ == '__main__':
    pass

    # Remove pass above to run test script: single-ended 1000 point data...
    #       colleciton and graphing
    gc = GC(True)

    print("Collecting 1000 data points...")
    gc.coll_volt_const_pts_self(1000)
    print("\nGraphing...")
    gc.graph_curr_data()
