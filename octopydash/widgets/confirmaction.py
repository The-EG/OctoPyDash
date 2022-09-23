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
from tkinter.font import Font
import logging

from octopydash.widgets.frame import Frame
from octopydash.widgets.button import ButtonBase

class ConfirmAction(tk.Toplevel):
    """
    A fullscreen 'dialog' window asking for confirmation of an action.

    This window will generate a custom event based on the user's choice:
      - Confirm - user clicked Confirm
      - Cancel  - user clicked Cancel
    """

    def __init__(self, parent, title, message, color='#7788ff', frame_loc='right'):
        """
        A fullscreen 'dialog' window asking for confirmation of an action.

        Parameters
        ----------
        parent : widget
            the parent widget/window for this dialog
        title : str
            a title to be shown at the top of the frame
        message : str
            a message to be shown at the middle of the window. can contain multiple lines
            of text.
        color : str
            the color of the frame. this can be any color that tkinter recognizes, 
            ie. 'red' or '#ff0000', default '#7788ff'
        frame_loc : str
            the location of the frame, either 'left' or 'right'. default 'right'
        """
        super().__init__(parent)
        self.grab_set()
        self.wm_attributes('-topmost', True)
        self.wm_attributes('-fullscreen',True)
        self._log = logging.getLogger(__name__)
        self.color = color
        self.title = title
        self.message = message
        self.frame_loc = frame_loc
        self._font_title = Font(self.master, size=22)
        self._font_msg = Font(self.master, size=30)
        self._map_id = self.bind('<Map>', self.on_map, '+')

    def on_map(self, event):
        self.frame = Frame(self, self.winfo_width(), self.winfo_height(), self.frame_loc, color=self.color)
        self.frame.pack(fill='both', expand=True)
        
        self.title_lbl = tk.Label(self, text=self.title, bg='#000000', fg=self.color, font=self._font_title)
        self.title_lbl.place(x=35 if self.frame_loc=='right' else self.winfo_width()-35, y=0, anchor='nw' if self.frame_loc=='right' else 'ne', height=40)

        self.message_lbl = tk.Label(self, text=self.message, bg='#000000', fg=self.color, font=self._font_msg)
        self.message_lbl['wraplength'] = self.winfo_width()-30
        self.message_lbl.place(x=(self.winfo_width()/2) + (10 * (-1 if self.frame_loc=='right' else 1)), y=(self.winfo_height()/2) - 20, width=self.winfo_width()-30, height=self.winfo_height()-140, anchor='center')

        self.confirm = ButtonBase(self, "CONFIRM", 80, color='#33cc99')
        self.confirm.bind("<<ButtonClick>>", self.on_confirm_click)
        self.confirm.place(x=35,y=self.winfo_height()-80)

        self.cancel = ButtonBase(self, 'CANCEL', 80, color='#dd4444')
        self.cancel.place(x=self.winfo_width()-35, y=self.winfo_height()-80, anchor="ne")
        self.cancel.bind("<<ButtonClick>>", self.on_cancel_click)

        self.unbind('<Map>', self._map_id)

    def on_confirm_click(self, event):
        self.event_generate("<<Confirm>>")
        self.destroy()

    def on_cancel_click(self, event):
        self.event_generate("<<Cancel>>")
        self.destroy()
