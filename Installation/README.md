# Folder for instructions on installation


### Auto Installation
I have made a [bash script](https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/install.sh) that will automatically install virtualenv, create a Python3 virtual environment, and install wxPython and GPIO within that virtual environment. The following versions were used in this installation.

|Package     | Version |
|:-----------|:--------|
| Python3 | 3.7.3 |
| virtualenv | 20.0.4 |
| pip | 18.1 |
| wxPython | 4.0.6 |

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
For the Linux savvy, go to town. The markdown files in this folder give the steps taken for each download/install. If you want to change which version of Python or wxPython, it is pretty straightforward but I cannot guarantee it will work.
