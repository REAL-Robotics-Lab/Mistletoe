# trajectory should be an Enum
from trajectory import Trajectory
from motor import Motor, MotorManager

class Leg:

    trajectory: Trajectory
    next_trajectory: Trajectory
    
    motor_manager: MotorManager

    hip_motor_id: int 
    knee_motor_id: int

    hip_motor: Motor
    knee_motor: Motor

    out_of_phase: bool

    def __init__(self, motor_manager, hip_motor_id, knee_motor_id, out_of_phase=False) -> None:
        self.motor_manager = motor_manager
        self.hip_motor_id = hip_motor_id
        self.knee_motor_id = knee_motor_id

        self.out_of_phase = out_of_phase

        self.hip_motor = motor_manager.get_motor(hip_motor_id)
        self.knee_motor = motor_manager.get_motor(knee_motor_id)

    def update(self):
        if self.trajectory.get_finished() == True:
            if self.next_trajectory != None:
                self.set_trajectory(self.next_trajectory)
        
    def set_trajectory(self, trajectory: Trajectory):
        if self.trajectory.get_finished() == True:
            self.trajectory = trajectory
        else:
            self.next_trajectory = trajectory

    def set_leg_position(self):
        if self.hip_motor.at_desired_position() and self.knee_motor.at_desired_position():
            self.trajectory.get_next_state()

            angle, velocity = self.trajectory.get_next_state()

            self.hip_motor.set_position(position=angle, velocity=velocity)
