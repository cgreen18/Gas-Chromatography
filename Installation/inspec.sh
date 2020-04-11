#!/bin/bash
# Creating gc Py3 virtualenv
cd /home/pi/
python3 -m venv --system-site-packages .gc_venv
# Enter virtualenv
source "/home/pi/.gc_venv/bin/activate"

echo "Installing dependencies"

# Upgrade pip
pip install -U pip

# Install dependencies
pip install -U six wheel setuptools

apt-get -y install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev

apt-get -y install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev

cd /home/pi/wxPython-4.0.6
pip3 install -r requirements.txt

echo "Building wxPython. Will take a long time ~2 hrs"

cd /home/pi/wxPython-4.0.6

python3 build.py build bdist_wheel --jobs=1 --gtk2
