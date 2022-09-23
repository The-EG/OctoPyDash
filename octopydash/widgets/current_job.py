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

from PIL import Image,ImageTk,ImageOps
from io import BytesIO

import requests

from octopydash.widgets.button import ButtonBase
from octopydash.widgets.files import FileList
from octopydash.widgets.confirmaction import ConfirmAction

class CurrentJob(tk.Frame):
    """Current job information (selected file, thumbnail, print, cancel, pause, files buttons)."""

    def __init__(self, parent, printer, width, height, bar_loc='left', color='#ffcc66'):
        """
        Current job information.

        Parameters
        ----------
        parent : widget
            the widget this widget will be contained in
        printer : Printer
            the OctoPrint printer client and socket
        width : int
        
        height : int

        bar_loc : str
            the location of the small bar/frame around the thumbnail. either 'left' or 'right'
            default 'left'
        color : str
            the color of the bar. any color that tkinter recognizes. default '#ffcc66'
        """
        super().__init__(parent)
        self.printer = printer
        self['width'] = width
        self['height'] = height
        self._log = logging.getLogger(f'{__name__} - {printer.name}')

        self.show_command = None
        self.hide_command = None
        self.should_show = True
        self.should_hide = False

        self._job_origin = None
        self._job_path = None

        self._pause_resume = False

        self.canvas = tk.Canvas(self, width=width, height=height, bg='#000000', bd=0, highlightthickness=0,relief='solid')
        self.canvas.place(x=0,y=0)
        
        bar_coords = [
            30, 10, # knot
            30, 10, # control
            10, 10, # control
            10, 10, # knot
            5, 10, # control
            0, 15, # control
            0, 20, # knot
            0, 20, # control
            0, height - 50 - 20, # control
            0, height - 50 - 20, # knot
            0, height - 50 - 15, # control
            5, height - 50 - 10, # control
            10, height - 50 - 10, # knot
            10, height - 50 - 10, # control
            30, height - 50 - 10, # control
            30, height - 50 - 10, # knot
            30, height - 50 - 10, # control
            30, height - 50 - 20, # control
            30, height - 50 - 20, # knot
            30, height - 50 - 20, # control
            20, height - 50 - 20, # control
            20, height - 50 - 20, # knot
            15, height - 50 - 20, # control
            10, height - 50 - 25, # control
            10, height - 50 - 30, # knot
            10, height - 50 - 30, # control
            10, 30, # control
            10, 30, # knot
            10, 25, # control
            15, 20, # control
            20, 20, # knot
            20, 20, # control
            30, 20, # control
            30, 20, # knot
        ]
        self.bar = self.canvas.create_polygon(bar_coords, fill=color, smooth='raw')
        if bar_loc=='right': self.canvas.scale(self.bar, width/2, 0, -1, 1)        

        self._file_img = tk.Label(self, bg='#000000')
        if bar_loc=='left': self._file_img.place(x=35, y= 10, width=width-40, height=height-10-50-10)
        else: self._file_img.place(x=width-35, y= 10, width=width-40, height=height-10-50-10, anchor='ne')

        self.file_lbl = tk.Label(self, bg='#000000', fg=color, text='')
        self.file_lbl.place(x=35 if bar_loc=='left' else width-35,y=5,anchor='nw' if bar_loc=='left' else 'ne')

        self.button_bar = tk.Frame(self, bg=color)
        self.button_bar.place(x=width/2, y=height-50, anchor='n')
        self.button_box = tk.Frame(self.button_bar, bg='#000000')
        self.button_box.pack(fill='both',expand=True, padx=10)

        self.print = ButtonBase(self.button_box, "PRINT", 50, 0, font_scale=1.0, color='#666688')
        self.print.pack(padx=(2,1), side='left')
        self.print.bind("<<ButtonClick>>", self.on_print_click)
        self.print.enabled = False

        self.pause = ButtonBase(self.button_box, "PAUSE", 50, 0, font_scale=1.0, color='#666688')
        self.pause.pack(padx=(1,1), side='left')
        self.pause.bind("<<ButtonClick>>", self.on_pause_click)
        self.pause.enabled = False

        self.cancel = ButtonBase(self.button_box, "CANCEL", 50, 0, font_scale=1.0, color='#666688')
        self.cancel.pack(padx=(1,1), side='left')
        self.cancel.bind("<<ButtonClick>>", self.on_cancel_click)
        self.cancel.enabled = False

        self.files = ButtonBase(self.button_box, "FILES", 50, 0, font_scale=1.0, color=color)
        self.files.bind("<<ButtonClick>>", self.on_files_click)
        self.files.pack(side='left', padx=(1,2))

        self.printer.socket.add_callback('current', self.on_current)
        self.printer.socket.add_callback('history', self.on_current)

    def on_print_click(self, event):
        self.printer.client.start_job()

    def on_pause_click(self, event):
        if self._pause_resume:
            self.printer.client.resume_job()
        else:
            self.printer.client.pause_job()

    def on_cancel_click(self, event):
        c = ConfirmAction(self, "Cancel Print?", "Are you sure you want to cancel the current print?", '#dd4444')
        c.bind("<<Confirm>>", lambda e: self.printer.client.cancel_job())

    def on_files_click(self, event):
        FileList(self, self.printer)

    def update_file(self):
        if self._job_path is None or self._job_origin is None:
            self.file_lbl['text'] = ''
            self._file_img['image'] = ''
            return

        (ret, file) = self.printer.client.file(self._job_origin, self._job_path)
        if ret:
            self.file_lbl['text'] = file['display']
            if 'thumbnail' in file:
                tn_url = self.printer.client.full_url(file['thumbnail'])
                r = requests.request('GET', tn_url)
                if r.status_code == 200:
                    img = Image.open(BytesIO(r.content))
                    sx = self._file_img.winfo_width() / img.width
                    sy = self._file_img.winfo_height() / img.height

                    self._tn_img = ImageTk.PhotoImage(ImageOps.scale(img, min(sx, sy)))
                    self._file_img['image'] = self._tn_img
                else:
                    self._log.warning("Couldn't get thumbnail: %s, %s", tn_url, r.status_code)

    def on_current(self, data):
        if data['state']['flags']['closedOrError'] and self.should_hide and self.hide_command:
            self.hide_command()
            self.should_hide = False
            self.should_show = True
        if data['state']['flags']['operational'] and self.should_show and self.show_command:
            self.show_command()
            self.should_show = False
            self.should_hide = True

        flags = data['state']['flags']
        if flags['operational'] and flags['ready'] and not flags['paused'] and not flags['printing'] and 'job' in data and data['job']['file']['path'] is not None:
            self.print.enabled = True
            self.print.set_color('#33cc99')
        else:
            self.print.enabled = False
            self.print.set_color('#666688')

        if flags['operational'] and (flags['printing'] or flags['paused']) and not flags['pausing'] and not flags['cancelling']:
            self.cancel.enabled = True
            self.cancel.set_color('#dd4444')
            if flags['paused']:
                self.pause.enabled = True
                self.pause.set_color('#33cc99')
                self._pause_resume = True
            else:
                self.pause.enabled = True
                self.pause.set_color('#ff7700')
                self._pause_resume = False
        else:
            self.cancel.enabled = False
            self.cancel.set_color('#666688')
            self.pause.enabled = False
            self.pause.set_color('#666688')
            

        if 'job' in data:
            path = data['job']['file']['path']
            origin = data['job']['file']['origin']

            if self._job_origin != origin or self._job_path != path:
                self._log.info('Job file changed %s|%s -> %s|%s', self._job_origin, self._job_path, origin, path)
                self._job_path = path
                self._job_origin = origin
                self.update_file()