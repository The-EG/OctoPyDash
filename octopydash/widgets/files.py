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
import requests
from PIL import Image,ImageTk,ImageOps
from io import BytesIO
import tkinter as tk
from tkinter.font import Font

from octopydash.widgets.frame import Frame
from octopydash.widgets.button import ButtonBase
from octopydash.widgets.confirmaction import ConfirmAction

class FileItem(tk.Frame):
    """A single file item shown in a FileList"""

    def __init__(self, parent, printer, file_info, width, height):
        """Create a FileItem widget

        Parameters
        ----------
        parent : widget
            the FileList this item will be contained in
        printer : printer
            the printer object this file item refers to (needed for client)
        file_info : dict
            OctoPrint file information
        width : int

        height : int

        """
        super().__init__(parent)
        self.printer = printer
        self.location = file_info['origin']
        self.path = file_info['path']
        self._log = logging.getLogger(f'{__name__}.FileItem - {printer.name}')
        self._width = width
        self._height = height
        self['width'] = width
        self['height'] = height
        self['bg'] = '#000000'

        self.file_info = file_info
        if 'prints' in self.file_info and self.file_info['prints']['last']['success']:
            self.color = '#33cc99'
        elif 'prints' in self.file_info and self.file_info['prints']['failure'] > 0:
            self.color = '#dd4444'
        else:
            self.color = '#f5f6fa'

        self.canvas = tk.Canvas(self, width=width, height=height, bg='#000000', bd=0, highlightthickness=0,relief='solid')
        self.canvas.pack()
        
        bar_coords = [
            width-225,0, # knot
            width-225,0, # control
            width-10,0, # control
            width-10,0, # knot
            width-5,0, # control
            width, 5, # control
            width, 10, # knot
            width, 10, # control
            width, height-10, #control
            width, height-10, # knot
            width, height-5, # control
            width-5, height, # control
            width-10, height, # knot
            width-10, height, # control
            width-225, height, # control
            width-225, height # knot
        ]
        self._right_bar = self.canvas.create_polygon(bar_coords, fill=self.color, smooth='raw')
        self._left_bar = self.canvas.create_rectangle(0, 0, 20, height, fill=self.color, outline=self.color)

        self._font = Font(self.master, size=int( ((height-20) * 0.75) * 0.33))

        name_x = 25 + height + 5

        self._file_name = self.canvas.create_text(name_x, height/2, anchor='w', text=self.file_info['display'], fill=self.color, font=self._font)

        if self.file_info['type']=='machinecode' and 'thumbnail' in self.file_info:
            url = self.printer.client.full_url(self.file_info['thumbnail'])
            r = requests.request('GET', url)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content))
                sx = self._height / img.width
                sy = self._height / img.height

                self._tn_img = ImageTk.PhotoImage(ImageOps.scale(img, min(sx, sy)))
                self.canvas.create_image(25, self._height/2, image=self._tn_img, anchor='w')
            else:
                self._log.warning("Couldn't get thumbnail: %s, %s", url, r.status_code)
                # set generic icon
        else:
            pass #set generic icon

        self.button_frame = tk.Frame(self, bg='#000000', height=height)
        self.button_frame.place(x=width-220, y=0)

        if (self.file_info['type']=='folder'):
            self.open_btn = ButtonBase(self.button_frame, "OPEN", self._height, 0, 0, color=self.color)
            self.open_btn.pack(side='left', padx=2)
            self.open_btn.bind("<<ButtonClick>>", self.on_open)
        else:
            self.select_btn = ButtonBase(self.button_frame, "SEL", self._height, 0, 0, color=self.color)
            self.select_btn.pack(side='left', padx=(2,1))
            self.select_btn.bind("<<ButtonClick>>", self.on_select)
            self.del_btn = ButtonBase(self.button_frame, "DEL", self._height, 0, 0, color=self.color)
            self.del_btn.pack(side='left', padx=(1,2))
            self.del_btn.bind("<<ButtonClick>>", self.on_delete)
        
    def on_open(self, event):
        self.event_generate("<<FolderOpened>>")
        
    def on_select(self, event):
        self._log.info("Selecting file: %s", self.path)
        (r, d) = self.printer.client.select_file(self.location, self.path)
        if r:
            self.event_generate("<<FileSelected>>")
        else:
            self._log.warning("Couldn't select file")
    
    def on_delete(self, event):
        def dodel(event):
            self._log.info("Deleting file: %s", self.path)
            (r, d) = self.printer.client.delete_file(self.location, self.path)
            if r:
                self.event_generate("<<FileDeleted>>")
            else:
                self._log.warning("Couldn't delete file")
        c = ConfirmAction(self, f"Delete file?", f"Are you sure you want to delete:\n{self.path}?")
        c.bind("<<Confirm>>", dodel)


class FileList(tk.Toplevel):
    """A list of files on the given OctoPrint server"""

    def __init__(self, parent, printer, color='#7788ff', frame_loc='right'):
        """Create a FileList for the given OctoPrint server
        
        Parameters
        ----------
        parent : widget

        printer : printer
        
        color : string, default='#7788ff'

        frame_loc : string, default='right'
        """
        super().__init__(parent, bg='#000000')
        self.grab_set()
        self.wm_attributes('-topmost', True)
        self.wm_attributes('-fullscreen',True)
        self.item_height = 80
        self._log = logging.getLogger(f'{__name__}.FileList - {printer.name}')
        self.color = color
        self.printer = printer
        self.frame_loc = frame_loc
        self._font_title = Font(self.master, size=22)
        self._font_msg = Font(self.master, size=30)
        self._map_id = self.bind('<Map>', self.on_map, '+')
        self._location = 'local'
        self._files = None
        self._file_items = []
        self._path = ''
        self._first_item = 0

    def on_map(self, event):
        self.frame = Frame(self, self.winfo_width(), self.winfo_height(), self.frame_loc, color=self.color, bottom_width=20, side_width=60)
        self.frame.pack(fill='both', expand=True)

        self.list_frame = tk.Frame(self, bg='#000000', width=self.winfo_width()-80, height=self.winfo_height()-100)
        self.list_frame.place(x=(self.winfo_width()/2) + (30 * (-1 if self.frame_loc=='right' else 1)), y=(self.winfo_height()/2) + 10, anchor='center', height=self.winfo_height()-100)

        self.item_width = self.winfo_width()-100
        self.max_show_items = int((self.winfo_height()-100) / self.item_height)
        
        self.title_lbl = tk.Label(self, text=f'{self.printer.name}: Files', bg='#000000', fg=self.color, font=self._font_title)
        self.title_lbl.place(x=35 if self.frame_loc=='right' else self.winfo_width()-35, y=0, anchor='nw' if self.frame_loc=='right' else 'ne', height=40)

        self.close_btn = ButtonBase(self, "EXIT", color=self.color, font_scale=1.0)
        self.close_btn.bind("<<ButtonClick>>", self.on_close_click)
        self.close_btn.place(x=self.winfo_width()-85, y=0, anchor='ne')

        self.back_btn = ButtonBase(self, 'BACK', height=60, x_inset=0, y_inset=2, font_scale=0.5, color=self.color, width=60)
        self.back_btn.bind("<<ButtonClick>>", self.on_back)

        self.up_btn = ButtonBase(self, 'UP', height=60, x_inset=0, y_inset=2, font_scale=0.5, color=self.color, width=60)
        self.up_btn.bind("<<ButtonClick>>", self.on_up)

        self.down_btn = ButtonBase(self, 'DN', height=60, x_inset=0, y_inset=2, font_scale=0.5, color=self.color, width=60)
        self.down_btn.bind("<<ButtonClick>>", self.on_down)

        self.unbind('<Map>', self._map_id)
        self.update()
        self.goto_path('local','')

    def goto_path(self, location, path, first=0):
        self._location = location
        self._path = path
        self._first_item = first
        self.title_lbl['text'] = f'{self.printer.name}: {location}/{path}'
        (r, data) = self.printer.client.file(location, path)
        self._files = None
        if r and 'files' in data: self._files = data['files']
        elif r and 'children' in data: self._files = data['children']
        
        if path=='': self.back_btn.place_forget()
        else: self.back_btn.place(x=self.winfo_width(),y=60, anchor='ne')

        self._files.sort(key=lambda x: x['name'])
        self._files.sort(key=lambda x: -1 if x['type']=='folder' else 1)
        t = threading.Thread(target=self.update_list)
        t.run()

    def update_list(self):
        self._log.debug("Starting update_list thread")
        for child in self._file_items:
            child.pack_forget()
        
        if self._files is None:
            self._log.warning("Can't show files, none found?")
            return

        range(self._first_item)
        for fi in range(self._first_item, self._first_item + self.max_show_items):
            if fi >= len(self._files): break
            file = self._files[fi]
            fi = FileItem(self.list_frame, self.printer, file, self.item_width, self.item_height)

            fi.bind('<<FileSelected>>', lambda e: self.destroy())
            fi.bind("<<FileDeleted>>", lambda e: self.goto_path(self._location, self._path, self._first_item))
            fi.bind("<<FolderOpened>>", lambda e: self.goto_path(self._location, e.widget.path))
            fi.pack(pady=2)
            self.update()
            self._file_items.append(fi)

        if self._first_item > 0:
            self.up_btn.place(x=self.winfo_width(),y=120, anchor='ne')
        else:
            self.up_btn.place_forget()
        
        if len(self._files) - self._first_item > self.max_show_items:
            self.down_btn.place(x=self.winfo_width(),y=self.winfo_height()-120, anchor='ne')
        else:
            self.down_btn.place_forget()

        self._log.debug("End update_list thread")

    def on_back(self, event):
        parts = self._path.split('/')
        self.goto_path(self._location, '/'.join(parts[:-1]))
        
    def on_up(self, event):
        self._first_item -= self.max_show_items
        if self._first_item < 0: self._first_item = 0
        self.update_list()

    def on_down(self, event):
        self._first_item  += self.max_show_items
        self.update_list()

    def on_close_click(self, event):
        self.destroy()