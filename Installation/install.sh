#!/bin/bash
#install.sh


echo "Install script to set up a new Raspberry Pi to collect gc data and run the gc suite upon startup."
echo "Install instructions given at https://github.com/cgreen18/Gas-Chromatography/tree/master/Installation"
echo "Tested on Raspberry Pi Model 3B+ w/ Raspbian 10 Buster"
echo "20 February 2020 Conor Green"

echo ""

echo "Updating repos"
cd ~
sudo apt-get update

echo "Installing and configuring virtualenv"

# Installing virtualenv
sudo apt-get install python3-venv
sudo pip install virtualenv
echo -e '\nexport PATH="/home/$USER/.local/bin:$PATH"' >> ~/.bashrc
cd ~/
source "./.bashrc"

# Creating gc Py3 virtualenv
python3 -m venv gc
# Enter virtualenv
source "./home/pi/gc/bin/activate


echo "Installing dependencies"

# Upgrade pip
pip install -U pip

# Install dependencies

apt-get update
pip install -U six wheel setuptools
apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
apt-get install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev


echo "Acquiring wxPython4.0.6"

# Get wxPython 4.0.6
wget https://files.pythonhosted.org/packages/9a/a1/9c081e04798eb134b63def3db121a6e4436e1d84e76692503deef8e75423/wxPython-4.0.6.tar.gz
tar xf wxPython-4.0.6.tar.gz

cd wxPython-4.0.6
pip3 install -r requirements.txt

echo "Building wxPython. Will take a long time ~2 hrs"
python3 build.py build bdist_wheel --jobs=1 --gtk2
