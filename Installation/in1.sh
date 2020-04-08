echo "Installing and configuring virtualenv"

# Installing virtualenv
sudo apt-get install python3-venv
sudo pip install virtualenv
echo -e '\nexport PATH="/home/$USER/.local/bin:$PATH"' >> ~/.bashrc
cd ~/
source "./.bashrc"
