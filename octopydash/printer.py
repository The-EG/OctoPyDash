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
import logging

from octopydash.octoclient import OctoClient
from octopydash.octosocket import OctoSocket

class Printer:
    """
    A representation of a Printer or OctoPrint instance.
    
    This is a convenient way to group both OctoPrint HTTP REST and
    websocket clients together. This class takes care of creating
    both and authenticating with the socket.

    The owner of this object is still responsible for starting and 
    stopping the socket connection.

    Attributes
    ----------
    name : str
        the name of this printer
    client : OctoClient
        the OctoPrint HTTP client
    socket : OctoSocket
        the OctoPrint websocket
    """
    
    def __init__(self, name, baseurl, apikey):
        """
        A representation of a printer or OctoPrint instance.

        Parameters
        ----------
        name : str
            the name of this printer
        baseurl : str
            the URL to the OctoPrint instance
        apikey : str
            the API Key to use when connecting to OctoPrint
        """
        self.name = name
        self._log = logging.getLogger(f'{__name__} - {name}')
        self.client = OctoClient(baseurl, apikey)
        self.socket = OctoSocket(baseurl.replace('http:','ws:'))
        self.socket.add_callback('connected', self.on_connected)

    def on_connected(self, data):
        self._log.info("Socket connected, logging in...")
        login = self.client.login()[1]
        self.socket.send_json({'auth': f'{login["name"]}:{login["session"]}'})
        