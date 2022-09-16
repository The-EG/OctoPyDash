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

class Frame(tk.Canvas):
    def __init__(self, parent, width, height, side_loc='right', top_width=40, side_width=10, bottom_width=80, color='#7788ff'):
        super().__init__(parent)
        self._log = logging.getLogger(__name__)
        self['bg'] = '#000000'
        self['bd'] = 0
        self['highlightthickness'] = 0
        self['relief'] = 'solid'
        self['height'] = height
        self['width'] = width

        radius = 10

        coords = [
            radius,                   0, # knot
            radius,                   0, # control
            width-radius,             0, # control
            width-radius,             0, # knot
            width-(radius/2),         0, # control
            width,           (radius/2), # control
            width,               radius, # knot
            width,               radius, # control
            width,        height-radius, # control
            width,        height-radius, # knot
            width,    height-(radius/2), # control
            width-(radius/2),    height, # control
            width-radius,        height, # knot
            width-radius,        height, # control
            radius,              height, # control
            radius,              height, # knot
            radius/2,            height, # control
            0,        height-(radius/2), # control
            0,            height-radius, # knot
            0,            height-radius, # control
            0, height - bottom_width + radius, # control
            0, height - bottom_width + radius, # knot
            0, height - bottom_width + (radius/2), # control
            radius/2, height - bottom_width, #control
            radius, height - bottom_width, # knot
            radius, height - bottom_width, # control
            width - side_width - radius, height - bottom_width, # control
            width - side_width - radius, height - bottom_width, # knot
            width - side_width - (radius/2), height - bottom_width, # control
            width - side_width, height - bottom_width - (radius/2), # control
            width - side_width, height - bottom_width - radius, # knot
            width - side_width, height - bottom_width - radius, # control
            width - side_width, top_width + radius, # control
            width - side_width, top_width + radius, # knot
            width - side_width, top_width + (radius/2), # control
            width - side_width - (radius/2), top_width, # control
            width - side_width - radius, top_width, # knot
            width - side_width - radius, top_width, # control
            radius, top_width, # control
            radius, top_width, # knot
            radius/2, top_width, # control
            0, top_width - (radius/2), # control
            0, top_width -radius, # knot
            0, top_width -radius, # control
            0, radius, # control
            0, radius, # knot
            0, (radius/2), # control
            (radius/2), 0, # control
            radius, 0, # knot
        ]
        self._poly = self.create_polygon(coords, fill=color, smooth='raw')
        if side_loc=='left': self.scale(self._poly, width/2, 0, -1, 1)