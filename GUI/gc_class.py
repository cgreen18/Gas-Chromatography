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
'''

# GPIO imports
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Multiprocessing
from multiprocessing import Process, Pipe

# Extra
import time

# Numpy and Matplotlib
import numpy as np
import matplotlib.pyplot as plt

class Gas_Chrom:
    # TODO:
    # Default single ended and make differential a keyword arg

    def __init__(self, single_ended):
        self.__version__ = '1.3'
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
        self.curr_data = np.array([])
        self.prev_runs = None
        self.run_num = 0


    def main(self):
        pass

    # Can be called concurrently with the indefinite data collection
    def end_data_coll(self):
        self.allow_coll_data = False

    def begin_data_coll(self, child_conn, ref_rt):
        self.allow_coll_data = True
        self.coll_indefinite_data(now, child_conn , ref_rt)

    def coll_indefinite_data(self, conn, refresh_rate):
        sampling_period = refresh_rate
        epsilon = 0.001 #sec

        volt_and_time =  np.zeros((2 , 1) ) #dtype=float )

        t_start = time.time()
        while self.allow_coll_data:
            t_last = volt_and_time[1][i-1]

            t_curr = time.time()

            #TODO: Clean up that logic
            while (t_curr - epsilon -t_last > sampling_period) or (t_curr + epsilon - t_last < sampling_period):
                time.sleep(.0001)
                t_curr = time.time()
            #Past loop therefore sample
            volt_and_time[0][i] = self.get_voltage()
            volt_and_time[1][i] = t_curr - t_last
            self.curr_data = volt_and_time

            conn.send(self.curr_data)
            conn.close()


    # Temporary graphing methods
    def graph_curr_data(self):
        plt.figure()
        plt.scatter(self.curr_data[1][:], self.curr_data[0][:])
        plt.show()

    # Numpy/data methods
    def coll_volt_const_pts(self , num_pts):
        voltage_and_time =  np.zeros((2 , num_pts ) ) #dtype=float )

        t_start = time.time()
        for i in range(0,num_pts):
            time.sleep(.01)
            voltage_and_time[0][i] = self.get_voltage()
            t_curr = time.time()
            voltage_and_time[1][i] = t_curr - t_start

        return voltage_and_time

    def coll_volt_const_pts_self(self, num_pts):
        self.run_num += 1
        self.prev_runs.append(self.curr_data)
        self.curr_data = self.coll_volt_const_pts(num_pts)
        print(self.curr_data)

    def get_curr_data(self):
        return self.curr_data


    # ADS1115 Methods
    def reinit_ADS(self):
        self.i2c = busio.I2C(board.SCL , board.SDA)
        self.ads = ADS.ADS1115(self.i2c)

        self.chan = AnalogIn(ads , self.port0) if self.single_ended else AnalogIn(ads, self.port0 , self.port1)

    def set_gain(self, gain):
        self.ads.gain = gain

    def set_mode(self, single_ended):
        self.single_ended = single_ended

        self.reinit_ADS()

    def print_voltage(self):
        print(self.chan.voltage)

    def print_value(self):
        print(self.chan.value)

    def get_voltage(self):
        return self.chan.voltage

    def get_value(self):
        return self.chan.value

if __name__ == '__main__':
    gc = Gas_Chrom(True)

    print("Collecting 1000 data points")
    gc.coll_volt_const_pts_self(1000)
    print("Graphing")
    gc.graph_curr_data()
