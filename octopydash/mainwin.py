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
import tkinter as tk
import logging

from octopydash.printer import Printer

from octopydash.widgets import PrinterStatus, Frame, PSUControlPower, CurrentJob

class MainWin(tk.Tk):
    def __init__(self):
        super().__init__()
        self._log = logging.getLogger(__name__)
        self.wm_title('OctoPyDash')
        self.wm_attributes('-fullscreen',True)
        self['bg'] = '#000000'
        self.protocol('WM_DELETE_WINDOW', self.on_exit)

        self._map_id = self.bind('<Map>', self.on_map, '+')


    def on_map(self, event):
        self._log.info('Creating widgets...')

        # Change these to configure your printers
        self.printer_a = Printer("Printer A Name", "http://printer-a-url", "PRINTERAPIKEY")
        self.printer_b = Printer("Printer B Name", "http://printer-b-url", "PRINTERAPIKEY")

        height = self.winfo_height()
        width = self.winfo_width()

        self.printera_frame = Frame(self, (width/2)-2, height, 'right', color='#88ccff')
        self.printera_frame.place(x=0,y=0)

        self.printera_status = PrinterStatus(self, self.printer_a, 40, color='#88ccff')
        self.printera_status.place(x=20, y=0)

        self.printera_buttons = tk.Frame(self, bg='#000000')
        self.printera_buttons.place(x=20, y=height-80)

        self.printera_power = PSUControlPower(self.printera_buttons, self.printer_a, 80, 0)
        self.printera_power.pack(side='left', padx=(2,2))

        self.printera_job = CurrentJob(self, self.printer_a, (width/2)-32, height-140)
        self.printera_job.show_command = lambda: self.printera_job.place(x=10, y=50)
        self.printera_job.hide_command = lambda: self.printera_job.place_forget()

        self.printerb_frame = Frame(self, (width/2)-2, height, 'left', color='#ffcc66')
        self.printerb_frame.place(x=(width/2)+2, y=0)

        self.printerb_status = PrinterStatus(self, self.printer_b, 40, color='#ffcc66')
        self.printerb_status.place(x=width-20, y=0, anchor='ne')

        self.printerb_power = PSUControlPower(self, self.printer_b, 80)
        self.printerb_power.place(x=width-20, y=height-80, anchor='ne')

        self.printerb_job = CurrentJob(self, self.printer_b, (width/2)-32, height-140, 'right')
        self.printerb_job.show_command = lambda: self.printerb_job.place(x=width - 10, y=50, anchor='ne')
        self.printerb_job.hide_command = lambda: self.printerb_job.place_forget()

        self._log.info('Starting up sockets...')

        self.printer_a.socket.connect()
        self.printer_b.socket.connect()
        self.unbind('<Map>', self._map_id)

    def on_exit(self):
        self.printer_a.socket.close()
        self.printer_b.socket.close()
        self.destroy()