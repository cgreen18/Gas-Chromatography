#!/bin/bash
# start.sh

cd /home/pi
source "/home/pi/gc/bin/activate"

cd Gas-Chromatography/GUI

python gc_gui.py

