# Extra Libraries
### Important: All these must be install while the virtual environment is active
```
source /home/pi/.gc_venv/bin/activate
```

Update pip and tools for building a wheel (for use later)
```
pip install -U pip
pip install -U six wheel setuptools
```

Install some libraries
```
apt-get -y install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
apt-get -y install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev
```

More
```
apt-get install libatlas-base-dev
```

```
pip3 install matplotlib
```

```
pip3 install pyyaml
```
