from typing import Dict
import moteus

class MotorState:
    position: float

    def update(self, state: Dict):
        self.position = state.values[moteus.Register.POSITION]

    def get_angle(self):
        return self.position * 360
    
    def __repr__(self) -> str:
        return f'Position: {self.get_angle()}'
