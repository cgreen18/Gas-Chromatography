# !/bin/bash

printf "%-120s\n" "-------------------------------------------------------------------------------------------------------------------"
printf "%-120s\n" "| Configuration script to install the required dependencies for Gas-Chromatography on a new Raspberry Pi."
printf "%-120s\n" "| Instructions given at https://github.com/cgreen18/Gas-Chromatography/blob/master/Installation/Configuration.md"
printf "%-120s\n" "| Tested on Raspberry Pi Model 3B+ w/ Raspbian 10 Buster"
printf "%-120s\n" "| Functions as intended as of 10 April 2020"
printf "%-120s\n" "| Conor Green and Matt McPartlan"
printf "%-120s\n" "-------------------------------------------------------------------------------------------------------------------"

sleep 10s

printf "\n\n\n\n\n\n\n\n\n"

# Root privileges check
if (( $EUID != 0 )); then
    printf "Please run as root (i.e. sudo ./config.sh)\n"
    exit
fi
# to configure auto-start programs and allow SPI/SCI
printf "\n ""Enabling Serial in raspi-config"
# Enable SPI and SCI from raspi-config
raspi-config nonint do_serial 0
cat /boot/cmdline.txt

printf "Enabling I2C and SPI in raspi-config\n"
# Enable SPI and SCI from raspi-config
raspi-config nonint do_i2c 0
raspi-config nonint do_spi 0

printf "\n""Configuring 'gas_chromatograph.py' to autorun at startup via .bashrc\n"
# Default gc_venv
echo '\n#Probably bad style to have 5 lines in .bashrc but this RPi is dedicated to GC, so oh well.' >> /home/pi/.bashrc
echo '\nsource "/home/pi/gtest/bin/activate"' >> /home/pi/.bashrc
echo '\ncd /home/pi/Gas-Chromatography' >> /home/pi/.bashrc
echo '\ncat README.md' >> /home/pi/.bashrc
echo '\ncd /home/pi/Gas-Chromatography/GUI/current_version' >> /home/pi/.bashrc
echo '\npython3 gas_chromatography.py' >> /home/pi/.bashrc
