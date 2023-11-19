from typing import Dict
import moteus

class MotorState:
    position: float
    offset: float

    def __init__(self, offset=0):
        self.offset = offset

    def update(self, state: Dict):
        self.position = state.values[moteus.Register.POSITION]

    def get_angle(self):
        return self.position * 360
    
    def get_offsetted_angle(self, angle):
        return angle + self.offset
    
    def __repr__(self) -> str:
        return f'Position: {self.get_angle()}'
