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
import requests
import logging

class OctoClient:
    """
    An OctoPrint HTTP client.
    
    Methods
    -------
    full_url : return the full url for a given path
    plugin_simple_api_command : perform a plugin simple api command
    psucontrol_turn_on : (PSU Control Plugin) turn on PSU
    psucontrol_turn_off : (PSU Control Plugin) turn off PSU
    version : return OctoPrint version information
    login : perform a passive login
    file : return file or folder information
    select_file : select a file for printing
    delete_file : delete a file
    start_job : start the print job
    pause_job : pause the print
    resume_job : resume from pause
    cancel_job : cancel print
    """

    def __init__(self, baseurl, apikey):
        """
        An OctoPrint HTTP Client

        Parameters
        ----------
        baseurl : str
            the URL to the OctoPrint instance
        apikey : str
            the API Key to use when connecting to OctoPrint
        """
        self._url = baseurl
        self._apikey = apikey
        self._hdrs = {'X-Api-Key': apikey}
        self._log = logging.getLogger(f'{__name__} - {baseurl}')
        self._log.debug("init for %s with %s", baseurl, apikey)

    def _do_request(self, url, method='GET', data=None):
        try:
            r = requests.request(method, f'{self._url}{url}', headers=self._hdrs, json=data, timeout=30)
        except:
            self._log.error(f"Couldn't make request to {url}")
            return (False, None)
        if 200 <= r.status_code < 300:
            self._log.info(f'{url} -> {r.status_code}')
            try:
                return (True, r.json())
            except requests.exceptions.JSONDecodeError:
                return (True, None)
        else:
            self._log.warn(f'{self._url}{url} -> {r.status_code}')
            return (False, r.status_code)

    def full_url(self, path):
        """
        Return the full url for a given `path`.

        Returns the full url for a given `path`. For example, if 
        `path` is '/api/files' this method will return 'http://baseurl/api/files'.

        Parameters
        ----------
        path : str

        Returns
        -------
        str
        """
        return f'{self._url}{"/" if path[0] != "/" else ""}{path}'

    def plugin_simple_api_command(self, plugin, data):
        """
        Perform a plugin simple api command.

        Parameters
        ----------
        plugin : str
            the id of the plugin
        data : dict
            the data to pass to the simple api command. this must include a 
            'command' member

        Returns
        -------
        success : bool
            indicates success or failure
        data : dict, None, or int
            Data returned if any or the HTTP response code on failure
        """
        return self._do_request(f'/api/plugin/{plugin}', 'POST', data)

    def psucontrol_turn_on(self):
        """
        (PSU Control Plugin) Turn on PSU.

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None or the HTTP response code on failure
        """
        return self.plugin_simple_api_command('psucontrol', {'command':'turnPSUOn'})

    def psucontrol_turn_off(self):
        """
        (PSU Control Plugin) Turn off PSU.

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None or the HTTP response code on failure
        """
        return self.plugin_simple_api_command('psucontrol', {'command':'turnPSUOff'})

    def version(self):
        """
        Return OctoPrint version information.

        Returns
        -------
        success : bool
            indicates success or failure
        data : dict or int
            the octoprint version info on success or the HTTP response code on failure
        """
        return self._do_request('/api/version')

    def login(self):
        """
        Perform a passive login using the api key supplied with this client.

        Returns
        -------
        success : bool
            indicates success or failure
        data : dict or int
            the octoprint session info on success or the HTTP response code on failure
        """
        return self._do_request('/api/login', 'POST', {'passive': True})

    def file(self, location, path):
        """
        Return file or folder information.

        Parameters
        ----------
        location : str
            the location or origin. should be one of: 'sdcard', 'local'
        path : str
            the path of the file or folder. may be None or '' to get the root folder

        Returns
        -------
        success : bool
            indicates success or failure
        data : dict or int
            the file or folder info on success or the HTTP response code on failure            
        """
        if path is not None and len(path) > 0: return self._do_request(f'/api/files/{location}/{path}')
        else: return self._do_request(f'/api/files/{location}')

    def select_file(self, location, path):
        """
        Select a file for printing.

        Parameters
        ----------
        location : str
            the location or origin. should be one of: 'sdcard', 'local'
        path : str
            the path of the file

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None on success or the HTTP response code on failure            
        """
        return self._do_request(f'/api/files/{location}/{path}', 'POST', {'command':'select'})

    def delete_file(self, location, path):
        """
        Delete a file.

        Parameters
        ----------
        location : str
            the location or origin. should be one of: 'sdcard', 'local'
        path : str
            the path of the file

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None on success or the HTTP response code on failure
        """
        return self._do_request(f'/api/files/{location}/{path}','DELETE')

    def start_job(self):
        """
        Start the print job.

        Start the currently selected file. A file must already be slected.

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None on success or the HTTP response code on failure
        """
        return self._do_request(f'/api/job', 'POST', {'command':'start'})

    def pause_job(self):
        """
        Pause the currently running print.

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None on success or the HTTP response code on failure
        """
        return self._do_request(f'/api/job', 'POST', {'command':'pause', 'action': 'pause'})

    def resume_job(self):
        """
        Resume the currently paused print.

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None on success or the HTTP response code on failure
        """
        return self._do_request(f'/api/job', 'POST', {'command':'pause', 'action':'resume'})

    def cancel_job(self):
        """
        Cancel the currently running print.

        Returns
        -------
        success : bool
            indicates success or failure
        data : None or int
            None on success or the HTTP response code on failure
        """
        return self._do_request(f'/api/job', 'POST', {'command':'cancel'})