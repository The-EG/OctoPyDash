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
import tkinter as tk
from tkinter.font import Font

class PrinterStatus(tk.Canvas):
    def __init__(self, parent, printer, height=62, color='#7788ff'):
        super().__init__(parent)
        self.printer = printer
        self._log = logging.getLogger(f'{__name__} - {printer.name}')
        self.printer.socket.add_callback('current', self.on_current)
        self.printer.socket.add_callback('history', self.on_current)
        self._status_text = ''

        self['bg'] = '#000000'
        self['bd'] = 0
        self['highlightthickness'] = 0
        self['relief'] = 'solid'
        self['height'] = height
        self._color = color
        self._font = Font(self.master, size=int((height-10) * 0.75))
        self._name = self.create_text(10, height/2, anchor='w', text=self.printer.name, fill=self._color, font=self._font)

        name_width = self._font.measure(text=self.printer.name)
        sep_center = (10 + name_width + 15, height/2)

        self._sep = self.create_oval(sep_center[0]-5, sep_center[1]-5, sep_center[0]+5, sep_center[1]+5, fill=self._color)

        self._status_x = sep_center[0] + 15

        self._status = self.create_text(self._status_x, height/2, anchor='w', text='', fill=self._color, font=self._font)
        self.set_status_text('Unknown')

    def set_status_text(self, text):
        if text==self._status_text: return
        self._log.info(f'New Status: {text}')
        self.dchars(self._status, 0, 'end')
        self.insert(self._status, 0, text)
        self['width'] = self._status_x + self._font.measure(text=text) + 10
        self._status_text = text

    def on_current(self, data):
        self.set_status_text(data['state']['text'])