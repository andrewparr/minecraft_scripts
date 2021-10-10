import re
import asyncio
import logging
import json
import websockets
from websockets import WebSocketServerProtocol
from pygtail import Pygtail
import datetime

INTERVAL = 1
LOG_FILE = "/opt/minecraft/server/server/logs/latest.log"

logging.basicConfig(level=logging.INFO)

class Server:
    def __init__(self):
        self.clients = set()
        self.ON_LINE = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects.')
        jobj = json.dumps(list(self.ON_LINE))
        await ws.send(str(jobj))

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects.')

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def ws_handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            logging.info(f'I got the message: {message}')
            await self.send_to_clients(message)

    async def start(self) -> None:
        start_server = websockets.serve(self.ws_handler, '0.0.0.0', 4000)
        self.server = await start_server

    def stop(self) -> None:
        if self.server != None:
            self.server.close()

    async def monitor_log(self) -> None:
        joinedRegEx = re.compile("^.*: (.*) joined the game$")
        leftRegEx = re.compile("^.*: (.*) left the game$")
        pygtail = Pygtail(LOG_FILE, paranoid=True)
        while True:
            try:
                for line in pygtail:
                    x = joinedRegEx.search(line)
                    if x != None:
                        self.ON_LINE.add(x.group(1))
                    x = leftRegEx.search(line)
                    if x != None:
                        self.ON_LINE.discard(x.group(1))
                    jobj = json.dumps(list(self.ON_LINE))
                    now = datetime.datetime.now() + datetime.timedelta(hours=5)
                    print(str(jobj) + "  " + now.strftime('%H:%M:%S on %A, %B the %dth, %Y'))
                    await self.send_to_clients(str(jobj))
                await asyncio.sleep(INTERVAL)
            except OSError:
                await asyncio.sleep(INTERVAL)

try:
    server = Server()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(server.start(), server.monitor_log()))
    loop.run_forever()
except KeyboardInterrupt:
    server.stop()
