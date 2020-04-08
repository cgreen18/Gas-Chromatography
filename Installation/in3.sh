#!/bin/bash

# Enter virtualenv
source "/home/pi/.gc_venv/bin/activate"

echo "Installing dependencies"

# # Upgrade pip
# pip install -U pip

# Install dependencies
pip install -U six wheel setuptools
