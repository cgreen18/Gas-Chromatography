#!/bin/bash
#install.sh


echo "\nInstallation script to install the required dependencies for Gas-Chromatography on a new Raspberry Pi."
echo "Instructions given at https://github.com/cgreen18/Gas-Chromatography/tree/master/Installation"
echo "Tested on Raspberry Pi Model 3B+ w/ Raspbian 10 Buster"
echo "Functions as intended as of 10 April 2020"
echo "Conor Green and Matt McPartlan"
sleep 5s

echo "\n\n\n"

# Root privileges check
if (( $EUID != 0 )); then
    echo "Please run as root (i.e. sudo ./install.sh)"
    exit
fi

echo "Theres a general issue with \$USER becoming 'root' as opposed to 'pi'."
echo "This was fixed by hardcoding 'pi' user. There will be errors if the user is not pi and therefore no /home/pi/ directory."
echo "If you can fix this, please merge request or email me."

sleep 5s

echo "\n\n\n\n\n\n\n"

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


echo "Creating virtual environment: .gc_venv"
# Creating gc Py3 virtualenv
cd ./home/pi/
python3 -m venv --system-site-packages .gc_venv
source "/home/pi/.gc_venv/bin/activate"

echo "Installing dependencies"
# Upgrade pip
pip install -U pip
# Install dependencies
pip install -U six wheel setuptools
apt-get -y install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
apt-get -y install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev

echo "Acquiring wxPython4.0.6 (requires internet connection)"
# Get wxPython 4.0.6 to /home/pi
wget https://files.pythonhosted.org/packages/9a/a1/9c081e04798eb134b63def3db121a6e4436e1d84e76692503deef8e75423/wxPython-4.0.6.tar.gz -P /home/pi
cd /home/pi

echo "Unpacking wxPython tar"
tar -xf wxPython-4.0.6.tar.gz

echo "Installing requirements"
cd /home/pi/wxPython-4.0.6
pip3 install -r requirements.txt

echo "Building wxPython. Will take a long time ~2 hrs"
python3 build.py build bdist_wheel --jobs=1 --gtk2
