'''
Name: gc_gpio.py
Authors: Conor Green and Matt McPartlan
Description: Script to read analog input via ADS1115 A/D converter, as given in Adafruit tutorial (https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython).
Usage: For now call as main
Version:

'''

import board
import busio

import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn


def main():
    i2c = bus.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

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
