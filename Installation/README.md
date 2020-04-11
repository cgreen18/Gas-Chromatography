# Installation Wizard
### Hardware and Software
**Hardware**: Raspberry Pi Model 3B+ (armv71 32bit)

**OS**: Raspbian 10 Buster

|Package     | Version |
|:-----------|:--------|
| Python3 | 3.7.3 |
| virtualenv | 20.0.4 |
| pip | 18.1 |
| wxPython | 4.0.6 |

### Automatic Installation
First, clone the whole repo (https://github.com/cgreen18/Gas-Chromatography.git) into your home directory and navigate to the Installation folder.
```
cd ~
git clone https://github.com/cgreen18/Gas-Chromatography.git
cd Gas-Chromatography/Installation
```

Add executable permissions to the install script, ./install, and run the install script as root.
```
chmod +x ./install.sh
sudo ./install.sh
```

### Manual Installation
For the Linux savvy, go to town. The markdown files in this folder give the steps taken for each download/install. If you want to change which version of Python or wxPython, it is pretty straightforward but I cannot guarantee it will work.

[Virtualenv](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/Virtualenv.md) => [Libraries](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/Libraries.md) => [wxPython](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/wxPython.md)
