import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import builtins
from enum import Enum
import time

from typing import *

class Type(Enum):
    INTEGER = 0
    FLOAT = 1
    BOOLEAN = 2
    OPTION_DROPDOWN = 3

class Label:

    def __init__(self, text: str, value: type[int] | type[float] | type[bool]) -> None:
        self.frame = tk.Frame()
        self.name = text
        self.label = tk.Label(self.frame, text=f'{text}: ', font=('Arial', 15))
        self.input_var = None
        match type(value):
            case builtins.int:
                self.label_type = Type.INTEGER
            case builtins.float:
                self.label_type = Type.FLOAT
            case builtins.bool:
                self.label_type = Type.BOOLEAN
                self.input_var = tk.BooleanVar()
                self.input = tk.Checkbutton(self.frame, command=self._on_button_submit, variable=self.input_var)
            case _:
                self.label_type = Type.INTEGER

        self.label.pack(side=tk.LEFT)

        if self.label_type == Type.INTEGER or self.label_type == Type.FLOAT:
            self.input_var = tk.StringVar()
            self.input = tk.Entry(self.frame, width=5, textvariable=self.input_var, font=('Arial', 15))
            self.input.pack(side=tk.LEFT)
            self.update_button = tk.Button(self.frame, text='Update', command=self._on_button_submit, font=('Arial', 12))
            self.update_button.pack(side=tk.LEFT, padx=5)
        else:
            self.input.pack(side=tk.LEFT)

        self.frame.pack(pady=5)

        self.set_value(value)
        self.value = value

    def _on_button_submit(self):
        self.value = self._get_value()

    def _erroneous_input_msgbox(self):
        messagebox.showerror('Input Error', f'Erroneous input for variable: {self.name}')

    def _get_value(self):
        value = None
        match self.label_type:
            case Type.INTEGER:
                try:
                    value = int(self.input_var.get())
                except:
                    self.set_value(0)
                    self._erroneous_input_msgbox()
                    return -1
            case Type.FLOAT:
                try:
                    value = float(self.input_var.get())
                except:
                    self.set_value(0)
                    self._erroneous_input_msgbox()
                    return -1
            case Type.BOOLEAN:
                return self.input_var.get()
        return value

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.input_var.set(value)

class QuadUI:
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.labels: Dict[str, Label] = {}

        # style = ttk.Style(self.window)
        # style.configure('tkinter.ttk.Checkbutton', font = 40)

    def update(self):
        ui.window.update()

    def put(self, name, value: int | bool | float):
        if name in self.labels:
            self.labels[name].set_value(value)
        else:
            self.labels[name] = Label(name, value)

    def get(self, name) -> int | bool | float:
        if name in self.labels:
            return self.labels[name].get_value()
        return -1

    def mainloop(self):
        self.window.mainloop()

if __name__ == '__main__':
    ui = QuadUI()

    ui.put('Disabled', True)
    ui.put('Position', 5.0)
    try:
        while True:
            ui.put('Time', time.process_time())
            ui.update()
    except KeyboardInterrupt:
        pass