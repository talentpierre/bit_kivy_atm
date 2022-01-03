# BIT - Kivy Lightning ATM

## Requirements
- Raspberry Pi 4 (prefered)
- Monitor
- LNBits Wallet
- NV9 USB + (prefered)
- USB Cable (NV9 USB + - Raspberry Pi)
## Installation
Enter your terminal e.g. `STRG + ALT + T`
### 1. Clone Repos
```sh
cd
mkdir repos && cd repos
git clone https://github.com/talentpierre/bit_kivy_atm.git
git clone https://github.com/gmarull/nv9biller.git
```

### 2. Virtual environment
#### Updating pip
```sh
python3 -m pip install --upgrade pip setuptools virtualenv
```
#### Creating virtual env
```sh
cd
mkdir venv && cd venv
python3 -m virtualenv kivy_venv
```
#### Activating virtual env
```sh
cd
source venv/kivy_venv/bin/activate
```
### 3. Raspberry Pi dependencies 
#### Installation of basic dependencies
```sh
sudo apt update
sudo apt install pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   libgstreamer1.0-dev \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} libmtdev-dev \
   xclip xsel libjpeg-dev \
   libgirepository1.0-dev \
   libcairo2-dev
```
#### Installation of special dependencies
> Attention: You have to use different dependencies if you use ssh to work on your Pi. 
##### Installation of dependencies on a desktop environment
```sh
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```
##### Installation of dependencies via ssh/headless environment
[Kivy headless dependencies for Raspberry Pi](https://kivy.org/doc/stable/installation/installation-rpi.html#raspberry-pi-4-headless-installation-on-raspbian-buster])
##### Additional information if you use Raspberry Pi TouchScreen
[Kivy dependencies for TouchScreen](https://kivy.org/doc/stable/installation/installation-rpi.html#change-the-default-screen-to-use)

### 4. Kivy installation
> Note: Make sure you are in your virtual environment --> normally `(kivy_env)` at the beginning of your line
```sh
python -m pip install kivy[full] kivy_examples --no-binary kivy
````
### 5. Testing Kivy demo
```sh
cd
python venv/kivy_venv/share/kivy-examples/demo/showcase/main.py
```
### 6. Lightning ATM installation
```sh
cd ~/repos/bit_kivy_atm
pip install -r requirements.txt
```
### 7. NV9 USB + installation
```sh
cd ~/repos/nv9biller
pip install .
cp -r ~/repos/nv9biller/nv9biller ~/repos/bit_kivy_atm/
```
### 8. Configuration
- copy your media files (video (mp4), click sound(wav/mp3)) into the media file directory
- modify the `config.py` to match your naming
- create a `credential.py` and enter your credentials/url --> you can use the `example.credentials.py` as an example
### 9. Run the ATM
```sh
cd ~/repos/bit_kivy_atm
python main.py
```
