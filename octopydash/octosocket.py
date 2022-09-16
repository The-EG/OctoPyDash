# OctoPyDash - An OctoPrint Dashboard written in Python
# Copyright (C) 2022 Taylor Talkington

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import asyncio
import json
import logging
import websockets
import random
import string
import datetime
import threading
import queue    

class OctoSocket:
    def __init__(self, baseurl):
        self._log = logging.getLogger(f'{__name__} - {baseurl}')
        random.seed()
        server_code = random.randrange(100,999)
        session_code = ''.join(random.choices(string.ascii_lowercase, k=16))
        self._url = f'{baseurl}/sockjs/{server_code}/{session_code}/websocket'
        self._callbacks = {}
        self._should_close = False
        self._msg_queue = queue.Queue()
        self._last_hb = None

    async def _connect(self):
        async for websocket in websockets.connect(self._url):
            self._last_hb = None
            try:
                while not self._should_close:
                    if not self._msg_queue.empty():
                        msg = self._msg_queue.get()
                        await websocket.send(msg)
                    try:
                        message = await asyncio.wait_for(websocket.recv(), 0.2)
                        if message[0] == 'a':
                            msgs = json.loads(message[1:])
                            for m in msgs:
                                for msgtype in m:
                                    if msgtype in self._callbacks:
                                        for cb in self._callbacks[msgtype]:
                                            cb(m[msgtype])
                        elif message[0] == 'h':
                            self._log.info("socket heartbeat <3")
                            self._last_hb = datetime.datetime.now()
                    except asyncio.TimeoutError:
                        if self._last_hb is not None:
                            d = datetime.datetime.now() - self._last_hb
                            if d.total_seconds() > 60:
                                self._log.warning('watchdog triggered, reconnecting...')
                                await websocket.close()
                self._log.info("waiting for socket to close...")
                await websocket.close()
                self._log.info("socket closed.")
                return
            except websockets.ConnectionClosedError as ex:
                continue
            except websockets.ConnectionClosedOK as ex:
                continue

    def close(self):
        self._log.info("Signaling socket close...")
        self._should_close = True

    def add_callback(self, cb_type, callback):
        if cb_type not in self._callbacks:
            self._callbacks[cb_type] = []
        self._callbacks[cb_type].append(callback)

    def send_json(self, data):
        msg = json.dumps(data)
        msgarr = json.dumps([msg])
        self._msg_queue.put(msgarr)

    def connect(self):
        def run(): asyncio.run(self._connect())

        self.thread = threading.Thread(target=run)
        self.thread.start()
