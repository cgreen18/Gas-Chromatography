# Enable I2C, SPI and print README and run gas_chromatography.py at startup
###### Requires root privileges

### Enable Serial and confirm
Note, 0 is the first (not default iirc) option
For Serial, SCI, and SPI the first option (0) is 'enable'
```
sudo raspi-config nonint do_serial 0
cat /boot/cmdline.txt
```

### Enable i2c
