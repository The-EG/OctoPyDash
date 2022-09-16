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
    def __init__(self, baseurl, apikey):
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
        return f'{self._url}{"/" if path[0] != "/" else ""}{path}'

    def plugin_simple_api_command(self, plugin, data):
        return self._do_request(f'/api/plugin/{plugin}', 'POST', data)

    def psucontrol_turn_on(self):
        return self.plugin_simple_api_command('psucontrol', {'command':'turnPSUOn'})

    def psucontrol_turn_off(self):
        return self.plugin_simple_api_command('psucontrol', {'command':'turnPSUOff'})

    def version(self):
        return self._do_request('/api/version')

    def login(self):
        return self._do_request('/api/login', 'POST', {'passive': True})

    def file(self, location, path):
        if path is not None and len(path) > 0: return self._do_request(f'/api/files/{location}/{path}')
        else: return self._do_request(f'/api/files/{location}')

    def select_file(self, location, path):
        return self._do_request(f'/api/files/{location}/{path}', 'POST', {'command':'select'})

    def delete_file(self, location, path):
        return self._do_request(f'/api/files/{location}/{path}','DELETE')

    def start_job(self):
        return self._do_request(f'/api/job', 'POST', {'command':'start'})

    def pause_job(self):
        return self._do_request(f'/api/job', 'POST', {'command':'pause', 'action': 'pause'})

    def resume_job(self):
        return self._do_request(f'/api/job', 'POST', {'command':'pause', 'action':'resume'})

    def cancel_job(self):
        return self._do_request(f'/api/job', 'POST', {'command':'cancel'})