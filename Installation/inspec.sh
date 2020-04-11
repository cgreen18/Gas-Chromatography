#!/bin/bash
# Creating gc Py3 virtualenv
cd /home/pi/
source "/home/pi/.gc_venv/bin/activate"



echo "\nInstalling final libraries: atlas, matplotlib, PyYAML"
echo "Installing libatlas\n"
apt-get install libatlas-base-dev

echo "\nInstalling matplotlib\n"
pip3 install matplotlib

echo "\nInstalling PyYAML\n"
pip3 install pyyaml
