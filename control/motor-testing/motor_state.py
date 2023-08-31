from typing import Dict
import moteus

class MotorState:
    position: float
    trajectory_complete: bool

    def update(self, state: Dict):
        self.position = state[moteus.Register.POSITION]
        self.trajectory_complete = state[moteus.Register.TRAJECTORY_COMPLETE]

    def get_angle(self):
        return self.position * 360
    
    def __repr__(self) -> str:
        return f'Position: {self.position}\nTrajectory Complete: {self.trajectory_complete}'
