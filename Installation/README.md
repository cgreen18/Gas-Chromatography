# Install and Configure
### Hardware and Software
**Hardware**: Raspberry Pi Model 3B+ (armv71 32bit)

**OS**: Raspbian 10 Buster

|Package     | Version |
|:-----------|:--------|
| Python3 | 3.7.3 |
| virtualenv | 20.0.4 |
| pip | 18.1 |
| wxPython | 4.0.6 |

### Installation Wizard
Requires root privileges
First, clone the whole repo (https://github.com/cgreen18/Gas-Chromatography.git) into your home directory and navigate to the Installation folder.
```
cd ~
git clone https://github.com/cgreen18/Gas-Chromatography.git
cd Gas-Chromatography/Installation
```

Add executable permissions to the install script, ./install.sh, and run the install script as root.
```
chmod +x ./install.sh
sudo ./install.sh
```

Add executable permissions to the configuration script, ./config.sh, and run the install script as root.
```
chmod +x ./config.sh
sudo ./config.sh
```

### Manual Installation and Configuring
For the Linux savvy, go to town. The markdown files in this folder give the steps taken for each download/install. If you want to change which version of Python or wxPython, it is pretty straightforward but I cannot guarantee it will work.

[Virtualenv](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/Virtualenv.md) => [Libraries](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/Libraries.md) => [wxPython](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/wxPython.md) => [ADS1115](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/ADS1x15.md) => [Configure](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/Configuration.md)
