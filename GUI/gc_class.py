'''
Name: gc_class.py
Authors: Conor Green and Matt McPartlan
Description: Mid-level abstraction that will do most of the work. User interaction as well as data processing.
Usage: Call as main
Version:
1.0 - 26 January 20 - Initial creation. Skeleton to outline work for later
1.1 - 18 February 20 - Initialized and created some methods for ADS1115 and numpy
1.2 - 20 February 20 - Added methods for data collection and organizing self variables
1.2t - 21 February 20 - Debugged and works in preliminary testing!
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

class Gas_Chrom:
    # TODO:
    # Default single ended and make differential a keyword arg
    # Default P0 and P1 but allow arguments

    def __init__(self, single_ended):
        self.__version__ = '1.0'
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
        self.prev_runs = [self.curr_data]
        self.run_num = 0


    def main(self):
        pass

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

    # TODO:
    # Finish
    def set_pins(self, pin1, *args):
        #self.port0 =
        pass

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
