#!/bin/bash

echo "Acquiring wxPython4.0.6"
echo "Large download might take a while on slower processors or networks."

# Get wxPython 4.0.6
wget https://files.pythonhosted.org/packages/9a/a1/9c081e04798eb134b63def3db121a6e4436e1d84e76692503deef8e75423/wxPython-4.0.6.tar.gz -P /home/pi
cd /home/pi
tar -xf wxPython-4.0.6.tar.gz

cd /home/pi/wxPython-4.0.6
pip3 install -r requirements.txt

echo "Building wxPython. Will take a long time ~2 hrs"


source "/home/pi/.gc_venv/bin/activate"

cd /home/pi/wxPython-4.0.6

python3 build.py build bdist_wheel --jobs=1 --gtk2
