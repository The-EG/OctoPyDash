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

class ButtonBase(tk.Frame):
    def __init__(self, parent, text, height=40, x_inset=2, y_inset=0, font_scale=0.5, color='#ffcc66', width=None):
        super().__init__(parent)
        self._log = logging.getLogger(__name__)
        self.canvas = tk.Canvas(self, bg='#000000', bd=0, highlightthickness=0, relief='flat', height=height)
        self.canvas.pack()

        self.enabled = True

        self._color = color
        self._font = Font(self.master, size=int( ((height-20) * 0.75) * font_scale))
        w = self._font.measure(text=text) + 20
        self.canvas['width'] = width if width is not None else w 

        self._rect = self.canvas.create_rectangle(x_inset, y_inset, (width if width is not None else w ) - x_inset-1, height - y_inset-1, fill=self._color, outline=self._color)
        self._txt = self.canvas.create_text((width if width is not None else w )/2, height/2, text=text, fill='#000000', font=self._font)

        self.canvas.bind('<ButtonRelease-1>', self.on_click)

    def set_color(self, color):
        self.canvas.itemconfig(self._rect, fill=color, outline=color)
        
    def on_click(self, event):
        if self.enabled: self.event_generate("<<ButtonClick>>")
