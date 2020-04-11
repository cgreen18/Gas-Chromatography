#!/bin/bash

# Creating gc Py3 virtualenv
cd /home/pi/
python3 -m venv --system-site-packages .gc_venv
# Enter virtualenv
source "/home/pi/.gc_venv/bin/activate"
