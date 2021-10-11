import argparse
import asyncio
import json
import logging
import re
import time

import RPi.GPIO as GPIO
import websockets

# Edit this list to specify your friend minecraft user names with an associated GPIO pin
# for the corresponding LED.
# The ".*" is a catch up, which will light up if anyone in on the server.
users = {
    "user_1" : 8,
    "user_2" : 10,
    "user_3" : 12,
    ".*" : 16
}

logging.basicConfig(level=logging.INFO)

connections = []

async def consumer_handler(websocket: websockets.   WebSocketClientProtocol) -> None:
    try:
        async for message in websocket:
            logging.info(f"Message: {message}")
            on_line = json.loads(message)
            print(on_line)

            for n in users:
                pin = users[n]
                regex = re.compile(n)
                if any(regex.match(line) for line in on_line):
                    GPIO.output(pin, GPIO.HIGH)
                else:
                    GPIO.output(pin, GPIO.LOW)
    except Exception as e:
        print(repr(e))

async def consume(hostname: str, port: int) -> None:
    while True:
        try:
            websocket_resource_url = f"ws://{hostname}:{port}"
            async with websockets.connect(websocket_resource_url) as websocket:
                connections.append(websocket) 
                await consumer_handler(websocket)
        except ConnectionRefusedError:
            await asyncio.sleep(1)

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server", required=True, help="minecraft server")
ap.add_argument("-p", "--port", default=4000, help="port to use for websocket")
args = ap.parse_args()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Initialise the PINs are GPIO.OUT
for n in users:
    pin = users[n]
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume(hostname=args.server, port=args.port))
except KeyboardInterrupt:
    for c in connections:
        loop.run_until_complete(c.close())
