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
sudo apt-get install build-essential \ 
tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev \
libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
```
