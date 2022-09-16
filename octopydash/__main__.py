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
from octopydash.mainwin import MainWin

import logging

def_format = logging.Formatter('{asctime} - {name} - {levelname} - {message}', style='{')
def_handler = logging.StreamHandler()
def_handler.setLevel(logging.INFO)
def_handler.setFormatter(def_format)

logging.getLogger('').addHandler(def_handler)
logging.getLogger('').setLevel(logging.INFO)

# __name__ is __main__ when run as a module, not great for logging
log = logging.getLogger('octopydash.main')


log.info("                   OctoPyDash Startup")
log.info("============================================================")

win = MainWin()
try:
    win.mainloop()
except KeyboardInterrupt:
    log.info("Caught sigint, trying to close sockets...")
    win.on_exit()