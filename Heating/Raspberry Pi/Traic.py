'''
Title: Triac.py
Author: Conor Green
Description:
Usage:
Version:
'''

import RPi.GPIO as GPIO
import time

def init():
    GPIO.setmode(GPIO.BCM)

    z_c_pin = 23
    dig_pin = 24

    GPIO.setup(z_c_pin, GPIO.IN)

    GPIO.setup(dig_pin,GPIO.OUT,initial=GPIO.LOW)

    return

def main():
    while True:

        dimming = 100/1000000

        try:
            GPIO.wait_for_edge(z_c_pin,GPIO.FALLING)
            zero_cross(dimming)

        except KeyboardInterrupt:
            GPIO.cleanup()
            break



    GPIO.cleanup()
    return

def zero_cross(dimtime):

    time.sleep(dimtime)
    GPIO.output(dig_pin,GPIO.HIGH)
    time.sleep(10/1000000)
    GPIO.output(dig_pin,GPIO.LOW)

    return


if __name__ == '__main__':
    main()
