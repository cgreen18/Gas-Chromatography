#!/bin/bash
#install.sh

# Root privileges check
if (( $EUID != 0 )); then
    printf "\n""Please run as root (i.e. sudo ./install.sh)"
    exit
fi

printf "%-120s\n" "-------------------------------------------------------------------------------------------------------------------"
printf "%-120s\n" "| Installation script to install the required dependencies for Gas-Chromatography on a new Raspberry Pi."
printf "%-120s\n" "| Instructions given at https://github.com/cgreen18/Gas-Chromatography/tree/master/Installation"
printf "%-120s\n" "| Tested on Raspberry Pi Model 3B+ w/ Raspbian 10 Buster"
printf "%-120s\n" "| Functions as intended as of 10 April 2020"
printf "%-120s\n" "| Conor Green and Matt McPartlan"
printf "%-120s\n" "-------------------------------------------------------------------------------------------------------------------"

sleep 10s

printf "\n\n\n\n\n\n\n\n\n"


echo -e "\x1B[31Errors if /home/pi/ does not exist\e[0m"
echo "Theres a general issue with \$USER becoming 'root' as opposed to 'pi'."
echo "This was fixed by hardcoding 'pi' user."
echo "There will be errors if the user is not 'pi' and there is no /home/pi/ directory."
echo "If you can fix this, please merge request or email me."

sleep 5s

printf "\n\n\n\n\n\n\n"

echo -e "\e[4mUpdating repos\e[0m"

cd ~
sudo apt-get update

echo -e "\e[4mInstalling and configuring virtual environments\e[0m"
# Installing virtualenv
sudo apt-get install python3-venv
sudo pip install virtualenv
echo -e '\nexport PATH="/home/$USER/.local/bin:$PATH"' >> /home/pi/.bashrc
echo -e '\nexport PATH="/home/pi/.local/bin:$PATH"' >> /home/pi/.bashrc
source "/home/pi/.bashrc"


echo -e "\e[4mCreating virtual environment: .gc_venv\e[0m"
# Creating gc Py3 virtualenv
cd /home/pi/
python3 -m venv --system-site-packages .gc_venv
source "/home/pi/.gc_venv/bin/activate"

echo -e "\e[4mInstalling dependencies\e[0m"

apt-get update
# Upgrade pip
pip install -U pip
# Install dependencies
pip install -U six wheel setuptools

apt-get -y install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev

apt-get -y install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev libghc-gtk3-dev libwxgtk3.0-gtk3-dev

apt-get -y install python3.7-dev

echo -e "\e[4mAcquiring wxPython4.0.7.post2 (requires internet connection)\e[0m"
# Get wxPython 4.0.6 to /home/pi
wget https://files.pythonhosted.org/packages/b9/8b/31267dd6d026a082faed35ec8d97522c0236f2e083bf15aff64d982215e1/wxPython-4.0.7.post2.tar.gz

cd /home/pi

echo -e "\e[4mUnpacking wxPython tar\e[0m"
tar -xf wxPython-4.0.7.post2.tar.gz

echo -e "\e[4mInstalling requirements\e[0m"
cd /home/pi/wxPython-4.0.7.post2
pip3 install -r requirements.txt

echo -e "\e[4mBuilding wxPython. Will take a long time ~4 hrs\e[0m"

python3 build.py build bdist_wheel

echo -e "\e[4mInstalling final libraries: atlas, matplotlib, PyYAML\e[0m"
echo -e "\e[4mInstalling libatlas\e[0m"
apt-get install libatlas-base-dev

echo -e "\e[4mInstalling matplotlib\e[0m"
pip3 install matplotlib

echo -e "\e[4mInstalling PyYAML\e[0m"
pip3 install pyyaml
