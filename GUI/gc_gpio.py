
'''
Name: gc_gpio.py
Authors: Conor Green and Matt McPartlan
Description: Script to read analog input via ADS1115 A/D converter, as given in Adafruit tutorial (https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython).
            :
Usage: Call from gc_class to gather values
Copyright: Wrapper for library created by Adafruit and/or Carter Nelson at MIT. See Licences in the code at: Adafruit https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/tree/master/adafruit_ads1x15
Version:
1.0 - 24 January 2020 - Initial creation. Serves as test bed to read voltage values from ADS1115. Will be integrated into larger script.
1.1 - 18 February 2020 - Tested with a for loop in main. Found bug in defining bus
'''

import board
import busio

import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn

import time

class GCAnalogIn(AnalogIn):
    def __init__(self, **kwargs):
        gc_defaults = {}

        if is_diff:
            AnalogIn.__init__(self, ads, pos, neg)


def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

    chan = GCAnalogIn(ads,ADS.P0)


def single_ended():
    chan = AnalogIn(ads, ADS.P0)  #channel 1. For others use another pin

    print(chan.voltage)
    print(chan.value)

def differential():
    chan = AnalogIn(ads, ADS.P0, ADS.P1)

    print(chan.voltage)
    print(chan.value)

def set_gain(gain):
    ads.gain = gain

    print(chan.voltage)   #no change
    print(chan.value)     #will be amplified

if __name__ == '__main__':
    pass
