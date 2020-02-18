# Setting up wxPython
From [wxPython blog post](https://wxpython.org/blog/2017-08-17-builds-for-linux-with-pip/index.html)

### Get latest wxPython

```
pip download wxPython
```

Build the tar file, which may differ
```
pip wheel -v wxPython-4.0.7.post2.tar.gz  2>&1 | tee build.log

```

# OR
Follow [this post](https://wiki.wxpython.org/BuildWxPythonOnRaspberryPi)

### Dependencies
```
sudo apt-get update
sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
```

```
wget https://files.pythonhosted.org/packages/9a/a1/9c081e04798eb134b63def3db121a6e4436e1d84e76692503deef8e75423/wxPython-4.0.6.tar.gz
tar xf wxPython-4.0.6.tar.gz
```

```
sudo apt-get update
sudo apt-get install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev
```

```
cd wxPython-4.0.6
pip3 install -r requirements.txt
```

```
python3 build.py build bdist_wheel --jobs=1 --gtk2
```
