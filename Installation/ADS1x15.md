# Adafruit Tutorial
Installing and setting up the library is well described by Adafruit at their [Circuit Python on Raspberry Pi link](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/overview).

Copyright at end of document.

Make sure to do this in your [virtual environment](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/Virtual_Environment.md).

### Install Libraries
GPIO
```
pip3 install RPI.GPIO
```

blinka
```
pip3 install adafruit-blinka
```

### Enable I2C
Dependencies
```
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools
```

Change settings via raspi-config
```
sudo raspi-config
```

Navigate:
**Interfacing Options** -> **I2C** -> Enable **Yes**

```
sudo reboot
```

Test I2C w/
```
sudo i2cdetect -y 1
```

### Enable SPI

```
sudo raspi-config
```

Navigate: **Interfacing Options** -> **SPI** -> Enable **Yes**

```
sudo reboot
```

Test SPI w/
```
ls -l /dev/spidev*
```

The MIT License (MIT)

 Copyright (c) 2018 Carter Nelson for Adafruit

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
