#!/bin/bash
#install.sh


echo "Install script to install the required dependencies for Gas-Chromatography on a new Raspberry Pi."
echo "Install instructions given at https://github.com/cgreen18/Gas-Chromatography/tree/master/Installation"
echo "Tested on Raspberry Pi Model 3B+ w/ Raspbian 10 Buster"
echo "8 April 2020 Conor Green and Matt McPartlan"

echo ""

echo "Updating repos"
cd ~
sudo apt-get update

echo "Installing and configuring virtual environments"

# Installing virtualenv
sudo apt-get install python3-venv
sudo pip install virtualenv
echo -e '\nexport PATH="/home/$USER/.local/bin:$PATH"' >> /home/pi/.bashrc
echo -e '\nexport PATH="/home/pi/.local/bin:$PATH"' >> /home/pi/.bashrc
source "/home/pi/.bashrc"

# Creating gc Py3 virtualenv
echo "Creating virtual environment: .gc_venv"
cd ./home/pi/
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

echo "Acquiring wxPython4.0.6 (requires internet connection)"


# Get wxPython 4.0.6
wget https://files.pythonhosted.org/packages/9a/a1/9c081e04798eb134b63def3db121a6e4436e1d84e76692503deef8e75423/wxPython-4.0.6.tar.gz -P /home/pi
cd /home/pi

echo "Unpacking wxPython tar"

tar -xf wxPython-4.0.6.tar.gz

echo "Installing requirements"

cd /home/pi/wxPython-4.0.6
pip3 install -r requirements.txt

echo "Building wxPython. Will take a long time ~2 hrs"
python3 build.py build bdist_wheel --jobs=1 --gtk2
