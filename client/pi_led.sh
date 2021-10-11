#!/bin/bash
cd /home/pi/devel/minecraft_scripts/client
source ./env/bin/activate
python3 ./pi_led_client.py -s 10.10.10.10
