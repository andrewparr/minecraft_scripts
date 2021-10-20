# Minecraft log watching script
Allows a Raspberry pi to light up LEDs when users connect to a Minecraft server.

## Table of Contents
* [General Info](#general-information)
* [Setup](#setup)
* [Usage](#usage)

## General Information
A script running on the machine running the Java minecraft server will monitor the generated
log file for people connecting / disconnecting from the server.  This provides a simple
websocket API.
A script running on a Raspberry Pi will connect to this server and light specific LEDs for certain users.

## Setup

On the server (in a tmux window)
```
cd ~
git clone https://github.com/andrewparr/minecraft_scripts.git
cd ~/minecraft_scripts/server
sudo apt-get install python3-venv
python3 -m venv env
source ./env/bin/activate
pip3 install pygtail
pip3 install websockets
python3 log_watcher.py -l <PATH OF MINECRAFT INSTALL>/logs/latest.log -p 4000
```

For a quick test, in a different tmux window
```
cd ~/minecraft_scripts
python3 -m http.server
```
Then in your browser, going to `http://<ip server>:8000` will show a page listing who is currently connected to the minecraft server.
This page will be updated as people connect or disconnect from the server.

On a Raspberry Pi.
```
sudo apt-get install python-rpi.gpio python3-rpi.gpio
cd ~
git clone https://github.com/andrewparr/minecraft_scripts.git
cd ~/minecraft_scripts/client
```
At this point you should edit the pi_led_client.py script.
At the top you'll see a list of Minecraft usernames, edit this to include your friend minecraft names.

Then follow these steps to create a service to run this script when the pi starts up.
```
python3 -m venv env
source ./env/bin/activate
pip install RPi.GPIO
sudo systemctl daemon-reload
sudo systemctl enable pi_led.service
systemctl status pi_led.service
```

## Usage
