import moteus
from typing import Dict, Any
import asyncio

class Motor:
    _position: float
    offset: float
    controller: moteus.Controller
    
    def __init__(self, controller, offset=0) -> None:
        self.controller = controller
        self.offset = offset
        self._position = 0

    def update_status(self, state: Dict) -> None:
        self._position = state.values[moteus.Register.POSITION]
    
    def zero_position(self) -> None:
        self.offset = self._position * 360
    
    def make_query(self) -> moteus.Command:
        return self.controller.make_brake(query=True)
    
    def make_position(self, **kwargs) -> moteus.Command:
        return self.controller.make_position(query=True, **kwargs)
    
    def make_stop(self) -> moteus.Command:
        return self.controller.make_stop()

    def get_position(self) -> float:
        return self._position - (self.offset/360)
    
    def get_angle(self) -> float:
        return self.get_position()*360

    def set_offset(self, offset_deg) -> float:
        self.offset = offset_deg
    
    def add_offset(self, offset_deg) -> float:
        self.offset += offset_deg
    
    def get_original_position(self) -> float:
        return self._position

    def __repr__(self) -> str:
        return f'Position: {self.get_angle()}'

