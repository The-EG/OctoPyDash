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
import threading
from octopydash.widgets.button import ButtonBase
from octopydash.widgets.confirmaction import ConfirmAction

class PSUControlPower(ButtonBase):
    """A button that indicates the status of and controls a PSU via the PSU Control plugin"""

    def __init__(self, parent, printer, height=40, x_inset=2, y_inset=0, font_scale=0.5):
        """
        A button that indicates the status of and controls a PSU via the PSU Control plugin
        
        Parameters
        ----------
        parent : widget
            the widget that this button will be contained in
        printer : Printer
            the OctoPrint client and socket
        height : int
            the height of the button, default 40
        x_inset : int
            the amount of padding to leave on the right and left sides of the button, default 2
        y_inset : int
            the amount of padding to leave on the top and bottom sides of the button, default 0
        font_scale : float
            a factor used to choose the font size based on the height of the button, default 0.5
        """
        super().__init__(parent, 'POWER', height, x_inset, y_inset, font_scale, '#666688')
        self.printer = printer
        self._is_on = False
        self._log = logging.getLogger(f'{__name__} - {printer.name}')

        self._color_unk = '#666688'
        self._color_off = '#dd4444'
        self._color_on = '#33cc99'
      
        self.printer.socket.add_callback('plugin', self.on_socket_plugin)

    def on_socket_plugin(self, data):
        if data['plugin'] == 'psucontrol':
            self._is_on = data['data']['isPSUOn']
            if self._is_on: 
                self.canvas.itemconfig(self._rect, fill=self._color_on, outline=self._color_on)
            else:
                self.canvas.itemconfig(self._rect, fill=self._color_off, outline=self._color_off)
        
    def on_click(self, event):
        if self._is_on:
            def turnoff(event):
                self.printer.client.psucontrol_turn_off()
                self._log.info("%s: On -> Off", self.printer.name)
            
            c = ConfirmAction(None, f'TURN OFF {self.printer.name}?', f'Turn off printer:\n{self.printer.name}?\nThis will terminate any active jobs.', '#dd4444')
            c.bind("<<Confirm>>", turnoff)
                
        else:
            t = threading.Thread(target=self.printer.client.psucontrol_turn_on)
            t.run()
            self._log.info("%s: Off -> On", self.printer.name)