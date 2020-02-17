# Folder for instructions on installation


### Auto Installation
I have made a [bash script](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/install.sh) that will automatically install virtualenv, create a Python3 virtual environment, and install wxPython and GPIO within that virtual environment.
Versions

|Package     | Version |
|:-----------|:--------|
|virtualenv | unknown|
| Python3 | 3.7.2 |
| wxPython | 4.0.6 |
| GPIO | | 

First, clone the whole repo (https://github.com/cgreen18/Gas-Chromatography) into your home directory and navigate to the Installation folder.
```
cd ~
git clone https://github.com/cgreen18/Gas-Chromatography
cd Gas-Chromatography/Installation
```

Add executable permissions to the install script, ./install, and run the install script as root.
```
chmod +x ./install.sh
sudo ./install.sh
```

### Manual Installation
For the 
