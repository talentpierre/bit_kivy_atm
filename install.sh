#!/bin/bash
home="/home/pi/"

# 1. Clone Repos
cd $home
mkdir repos venv
cd ~/repos_1
git clone https://github.com/talentpierre/bit_kivy_atm.git
git clone https://github.com/gmarull/nv9biller.git

# 2. Virtual environment
python3 -m pip install --upgrade pip setuptools virtualenv
cd ~/venv
python3 -m virtualenv kivy_venv
cd $home
source venv/kivy_venv/bin/activate

# 3. Raspberry Pi dependdencies
## Basic dependencies
sudo apt update
sudo apt install pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   libgstreamer1.0-dev \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} libmtdev-dev \
   xclip xsel libjpeg-dev \
   libgirepository1.0-dev \
   libcairo2-dev -y
## Special dependencies
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev -y

# 4. Kivy installation
python -m pip install kivy[full] kivy_examples --no-binary kivy

# 5. Testing Kivy demo
#cd $home
#python venv/kivy_venv/share/kivy-examples/demo/showcase/main.py

# 6. Lightning ATM installation
cd ~/repos/bit_kivy_atm
pip install -r requirements.txt

# 7. NV9USB+ installation
cd ~/repos/nv9biller
pip install .
cp -r ~/repos/nv9biller/nv9biller ~/repos/bit_kivy_atm/

# 8. Configuration
cd ~/repos/bit_kivy_atm/
mv example.credentials.py credentials.py

