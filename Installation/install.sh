#!/bin/bash
#install.sh

printf "%-120s\n" "-------------------------------------------------------------------------------------------------------------------"
printf "%-120s\n" "| Installation script to install the required dependencies for Gas-Chromatography on a new Raspberry Pi."
printf "%-120s\n" "| Instructions given at https://github.com/cgreen18/Gas-Chromatography/tree/master/Installation"
printf "%-120s\n" "| Tested on Raspberry Pi Model 3B+ w/ Raspbian 10 Buster"
printf "%-120s\n" "| Functions as intended as of 10 April 2020"
printf "%-120s\n" "| Conor Green and Matt McPartlan"
printf "%-120s\n" "-------------------------------------------------------------------------------------------------------------------"

sleep 10s

printf "\n\n\n\n\n\n\n\n\n"

# Root privileges check
if (( $EUID != 0 )); then
    printf "Please run as root (i.e. sudo ./install.sh)"
    exit
fi

printf "Theres a general issue with \$USER becoming 'root' as opposed to 'pi'."
printf "This was fixed by hardcoding 'pi' user. There will be errors if the user is not pi and therefore no /home/pi/ directory."
printf "If you can fix this, please merge request or email me."

sleep 5s

printf "\n\n\n\n\n\n\n"

printf "\nUpdating repos\n"

exit

cd ~
sudo apt-get update

printf "\nInstalling and configuring virtual environments\n"
# Installing virtualenv
sudo apt-get install python3-venv
sudo pip install virtualenv
echo -e '\nexport PATH="/home/$USER/.local/bin:$PATH"' >> /home/pi/.bashrc
echo -e '\nexport PATH="/home/pi/.local/bin:$PATH"' >> /home/pi/.bashrc
source "/home/pi/.bashrc"


printf "\nCreating virtual environment: .gc_venv\n"
# Creating gc Py3 virtualenv
cd ./home/pi/
python3 -m venv --system-site-packages .gc_venv
source "/home/pi/.gc_venv/bin/activate"

printf "\nInstalling dependencies\n"
# Upgrade pip
pip install -U pip
# Install dependencies
pip install -U six wheel setuptools
apt-get -y install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
apt-get -y install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev

printf "\nAcquiring wxPython4.0.6 (requires internet connection)\n"
# Get wxPython 4.0.6 to /home/pi
wget https://files.pythonhosted.org/packages/9a/a1/9c081e04798eb134b63def3db121a6e4436e1d84e76692503deef8e75423/wxPython-4.0.6.tar.gz -P /home/pi
cd /home/pi

printf "\nUnpacking wxPython tar\n"
tar -xf wxPython-4.0.6.tar.gz

printf "\nInstalling requirements\n"
cd /home/pi/wxPython-4.0.6
pip3 install -r requirements.txt

printf "\nBuilding wxPython. Will take a long time ~2 hrs\n"
python3 build.py build bdist_wheel --jobs=1 --gtk2

printf "\nInstalling final libraries: atlas, matplotlib, PyYAML"
printf "Installing libatlas\n"
apt-get install libatlas-base-dev

printf "\nInstalling matplotlib\n"
pip3 install matplotlib

printf "\nInstalling PyYAML\n"
pip3 install pyyaml
