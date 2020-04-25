#!/bin/bash
# start.sh

cd /home/pi
source "/home/pi/gtest/bin/activate"

cd Gas-Chromatography/GUI

python3 gas_chromatography.py
