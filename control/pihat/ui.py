import tkinter as tk
import builtins
from enum import Enum

from typing import *

class Type(Enum):
    INTEGER = 0
    FLOAT = 1
    BOOLEAN = 2
    OPTION_DROPDOWN = 3

class Label:

    def __init__(self, text: str, value: type[int] | type[float] | type[bool]) -> None:
        match type(value):
            case builtins.int:
                self.label_type = Type.INTEGER
            case builtins.float:
                self.label_type = Type.FLOAT
            case builtins.bool:
                self.label_type = Type.BOOLEAN
            case _:
                self.label_type = Type.INTEGER
        self.frame = tk.Frame()
        self.label = tk.Label(self.frame, text=f'{text}: ')
        self.input_var = tk.StringVar()
        self.input = tk.Entry(self.frame, width=5, textvariable=self.input_var)

        self.label.pack(side=tk.LEFT)
        self.input.pack(side=tk.LEFT)
        self.frame.pack(pady=5)

        self.set_value(value)

    def get_value(self):
        return self.value

    def update(self):
        value = None
        match self.label_type:
            case Type.INTEGER:
                try:
                    value = int(self.input_var.get())
                except:
                    return
        if value != self.value:
            print(value)
            self.value = value

    def set_value(self, value):
        self.value = value
        self.input_var.set(str(value))

class QuadUI:
    def __init__(self) -> None:
        self.window = tk.Tk('REAL Quad UI')
        self.labels: Dict[str, Label] = {}

    def update(self):
        for label in self.labels:
            self.labels[label].update()
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

    ui.put('Position', 5)
    try:
        while True:
            ui.update()
    except KeyboardInterrupt:
        pass