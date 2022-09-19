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
    """
    An OctoPrint websocket client.

    Methods
    -------
    connect : connect to the websocket
    close : close the websocket connection
    add_callback : add a message callback
    send_json : send a json message
    """

    def __init__(self, baseurl):
        """
        An OctoPrint websocket client.

        Parameters
        ----------
        baseurl : str
            the URL to the OctoPrint instance
        """
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
        """Close the websocket connection."""
        self._log.info("Signaling socket close...")
        self._should_close = True

    def add_callback(self, cb_type, callback):
        """
        Add a message callback.

        Add a callback function that will be called with data for
        each message recieved with the given `cb_type`.

        Parameters
        ----------
        cb_type : str
            a message type to attach this callback to. one of:
             - 'connected' - initial connection info
             - 'reauthRequired'
             - 'current' - general status update
             - 'history' - status and history sent upon intitial connection
             - 'event'
             - 'plugin'
             - 'slicingProgress'
        callback : function
            a function to call on the given `cb_type` event. should
            accept a single data parameter
        """
        if cb_type not in self._callbacks:
            self._callbacks[cb_type] = []
        self._callbacks[cb_type].append(callback)

    def send_json(self, data):
        """
        Send a json message across the websocket.

        Parameters
        ----------
        data : dict
            the data to be converted to json and sent
        """
        msg = json.dumps(data)
        msgarr = json.dumps([msg])
        self._msg_queue.put(msgarr)

    def connect(self):
        """Connect to the OctoPrint websocket."""
        def run(): asyncio.run(self._connect())

        self.thread = threading.Thread(target=run)
        self.thread.start()
