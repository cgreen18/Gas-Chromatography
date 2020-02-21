# Adafruit Tutorial
Installing and setting up the library is well described by Adafruit at their [Circuit Python on Raspberry Pi link](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/overview).

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

Test SPI w/
```
ls -l /dev/spidev*
```
