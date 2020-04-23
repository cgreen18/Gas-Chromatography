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

'''
@param: single_ended = True if single ended ADC and vice-versa
'''
class GC:
    def __init__(self, single_ended):
        self.__version__ = '2.0'
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
        self.indices = {'v':0,'area':1,'dt':2,'t':3}
        self.curr_data = np.zeros((self.dims, 0))
        self.curr_data_lock = Lock()
        self.time_out = 1 #sec
        self.epsilon = 0.01
        self.min_noise_after_norm = 0.2
        self.prev_runs = []
        self.run_num = 0

    def integrate_volt(self):
        to = self.time_out
        #ignore err for now
        _e = self.curr_data_lock.acquire(to)

        c_d = self.get_curr_data()
        _e = self.curr_data_lock.release()
        if len(c_d) != 0:
            voltage = self.get_volt()
            _l = 0
            _h = -1
            area = self.integrate(voltage, _l, _h)
            return area
        else:
            print("No data")

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

    def normalize_volt_(self):
        print("nomrlai")
        print(self.is_locked())
        to = self.time_out
        #ignore error for now
        _e = self.curr_data_lock.acquire(to)
        print('acquired volt')
        volt = self.get_volt()
        _e = self.curr_data_lock.release()

        _min = volt.min()
        volt = volt - _min

        _area = self.integrate_volt()
        volt = volt / _area

        _e = self.curr_data_lock.acquire(to)
        self.set_volt(volt)
        _e = self.curr_data_lock.release()

    def mov_mean_(self, window):
        _e = self.curr_data_lock.acquire(to)
        volt = self.get_volt()
        _e = self.curr_data_lock.release()

        np.convolve(vec, np.ones((window,))/window, mode='valid')

    def break_into_peaks(self):
        ep = self.epsilon
        if abs(self.integrate_volt() -1.0 ) > ep:
            self.normalize_volt_()

    def define_peaks(self):
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

    # ADS1115 Methods
    def reinit_ADS(self):
        self.i2c = busio.I2C(board.SCL , board.SDA)
        self.ads = ADS.ADS1115(self.i2c)

        self.chan = AnalogIn(ads , self.port0) if self.single_ended else AnalogIn(ads, self.port0 , self.port1)

    def set_gain(self, g):
        self.ads.gain = g

    def set_mode(self, se):
        self.single_ended = se
        self.reinit_ADS()

    # Getters and setters for locking
    def get_lock(self):
        return self.curr_data_lock

    def is_locked(self):
        _il = self.curr_data_lock.locked()
        return _il

    def get_curr_data(self):
        is_locked = self.is_locked()
        if is_locked:
            _d = np.copy(self.curr_data)
            return _d
        else:
            print('no access')

    def set_curr_data(self, d):
        is_locked = self.is_locked()
        if is_locked:
            d = np.copy(d)
            self.curr_data = d
        else:
            print('no access')

    def get_volt(self):
        is_locked = self.is_locked()
        v_index = self.indices['v']
        if is_locked:
            _v = np.copy(self.curr_data[v_index])
            return _v
        else:
            print('no access')

    def set_volt(self, d):
        is_locked = self.is_locked()
        v_index = self.indices['v']
        if is_locked:
            d = np.copy(d)
            self.curr_data[v_index] = d
        else:
            print('no access')

    def get_time(self):
        is_locked = self.is_locked()
        t_index = self.indices['t']
        if is_locked:
            _t = self.curr_data[t_index]
            return _t
        else:
            print('no access')

    def print_voltage(self):
        print(self.chan.voltage)

    def print_value(self):
        print(self.chan.value)

    def get_voltage(self):
        return self.chan.voltage

    def get_value(self):
        return self.chan.value

    # Temporary/old graphing methods
    def graph_curr_data_on_popup(self):
        plt.figure()
        to = self.time_out
        _e = self.curr_data_lock.acquire(to)
        t = self.get_time()
        v = self.get_volt()
        _e = self.curr_data_lock.release(to)
        plt.scatter( t, v )
        plt.show()

    # Numpy/data methods
    def coll_volt_const_pts(self , num_pts):
        v_i = self.indices['v']
        a_i = self.indices['area']
        dt_i = self.indices['dt']
        t_i = self.indices['i']

        temp_data_arr =  np.zeros((self.dims , num_pts ) )

        t_start = time.time()
        for i in range(0,num_pts):
            time.sleep(.01)
            temp_data_arr[v_i][i] = self.get_voltage()
            temp_data_arr[a_i] = None
            t_curr = time.time()
            temp_data_arr[dt_i][i] = t_curr - t_start
            temp_data_arr[t_i][i] = t_curr

        return voltage_and_time

    # old, dont trust
    def coll_volt_const_pts_self(self, num_pts):
        self.run_num += 1
        self.prev_runs.append(self.curr_data)
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
