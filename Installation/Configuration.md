# Enable I2C, SPI and print README and run gas_chromatography.py at startup
###### Requires root privileges

### GUI raspi-config
Enter raspi-config and manually enable serial, I2C, and SPI.

Or

### Enable Serial and confirm
Note, 0 is the first (not default iirc) option
For Serial, I2C, and SPI the first option (0) is 'enable'
```
sudo raspi-config nonint do_serial 0
cat /boot/cmdline.txt
```

### Enable I2C
```
sudo raspi-config nonint do_i2c 0
```

### Enable SPI
```
sudo raspi-config nonint do_spi 0
```

### Autorun gas_chromatography.py at startup
Add the following commands to your .bashrc (~/.bashrc).
Yes, it's a little weird to put this in the .bashrc but your computer is probably dedicated to GC. Otherwise, use a tasking daemon to initialize whenever or simply call manually.
###### Change these values:
<path_to_Gas-Chromatography_repo> is the absolute path in your computer to the Gas-Chromatography repository.
<path_to_gc_virtual_environment> is the absolute path to the python3 virtual environment to run the program.

```
source "<path_to_gc_virtual_environment>/bin/activate"
cd <path_to_Gas-Chromatography_repo>/GUI
python3 gas_chromatography.py
```
