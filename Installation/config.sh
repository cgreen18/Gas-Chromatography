# !/bin/bash
# config.sh
# to configure auto-start programs and allow SPI/SCI

# Enable SPI and SCI from raspi-config
# DOUBLE CHECK 1 IS CORRECT LATER
sudo raspi-config nonint do_serial 1
sudo raspi-config nonint do_serial 1

# Default gc_venv
echo -e '\nsource "/home/$USER/.gc_venv/bin/activate"' >> ~/.bashrc
