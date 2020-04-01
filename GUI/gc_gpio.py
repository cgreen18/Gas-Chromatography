
'''
Name: gc_gpio.py
Authors: Conor Green and Matt McPartlan
Description: Script to read analog input via ADS1115 A/D converter, as given in Adafruit tutorial (https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython).
Usage: Call as main
Version:
1.0 - 24 January 2020 - Initial creation. Serves as test bed to read voltage values from ADS1115. Will be integrated into larger script.
1.1 - 18 February 2020 - Tested with a for loop in main. Found bug in defining bus
'''

import board
import busio

import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn

import time


def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)


    chan = AnalogIn(ads,ADS.P0)

    for i in range(0,1000):
        print(chan.voltage)
        time.sleep(1)

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
    main()
