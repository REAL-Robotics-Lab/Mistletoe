from enum import Enum
from trajectory import Trajectory
from motor import Motor, MotorManager

class RotationSign(Enum):
    POSITIVE = 1
    NEGATIVE = 2

class Leg:

    trajectory: Trajectory
    next_trajectory: Trajectory

    counter: int
    traj_finished: bool
    
    motor_manager: MotorManager

    hip_motor_id: int 
    knee_motor_id: int

    hip_motor: Motor
    knee_motor: Motor

    out_of_phase: bool

    current_state: tuple[tuple[float, float], tuple[float, float]]

    def __init__(self, motor_manager, hip_motor_id, knee_motor_id, hip_inverted = False, knee_inverted = False, out_of_phase=False, hip_offset = 0 , knee_offset = 0) -> None:
        self.motor_manager = motor_manager
        self.hip_motor_id = hip_motor_id
        self.knee_motor_id = knee_motor_id

        self.hip_motor = self.motor_manager.get_motor(self.hip_motor_id)
        self.knee_motor = self.motor_manager.get_motor(self.knee_motor_id)

        self.hip_inverted = hip_inverted
        self.knee_inverted = knee_inverted

        self.out_of_phase = out_of_phase
        
        self.hip_motor.set_inverted(hip_inverted)
        self.knee_motor.set_inverted(knee_inverted)
        
        self.trajectory = None
        self.next_trajectory = None
        self.current_state = None

        self.hip_motor.set_offset(hip_offset)
        self.knee_motor.set_offset(knee_offset)

        self.counter = 0
        self.increment = 1
        self.traj_finished = False


    def update(self):
        self.counter += self.increment
        if self.counter >= self.trajectory.length:
            self.counter = 0
            self.traj_finished = True
        elif self.counter < 0:
            self.counter = self.trajectory.length-1
            self.traj_finished = True
        
        # print(self.hip_motor.get_status())
        # print(self.knee_motor.get_status())
        
        if self.trajectory is None or self.traj_finished:
            if self.next_trajectory != None:
                self.set_trajectory(self.next_trajectory)
        
        # print(self.trajectory.counter)

        if self.trajectory is not None:
            self.set_leg_position()
        
    def set_trajectory(self, trajectory: Trajectory, offset: float= 0, reversed: bool = False):
        if self.trajectory is None or self.traj_finished:
            self.trajectory = trajectory
            self.traj_finished = False
            true_offset = int(self.trajectory.length * offset)
            self.counter = true_offset if not reversed else (trajectory.length - 1) - true_offset
            self.increment = 1 if not reversed else -1
        else:
            self.next_trajectory = trajectory

    def set_leg_position(self):
        self.current_state = self.trajectory.get_state(self.counter)
        angles = self.current_state

        # TODO: should make these pos command params accessible through the constructor or something

        self.hip_motor.set_position(position=(angles[0]), velocity=0, maximum_torque=15, accel_limit=5, velocity_limit=10)
        self.knee_motor.set_position(position=(angles[1]), velocity=0, maximum_torque=15, accel_limit=5, velocity_limit=10)
        # else:
        #     angles, velocities = self.current_state

        #     self.hip_motor.set_position(position=(angles[0]), velocity=velocities[0], maximum_torque=12, accel_limit=2, velocity_limit=0.5)
        #     self.knee_motor.set_position(position=(-1 * angles[1]), velocity=velocities[1], maximum_torque=9, accel_limit=2, velocity_limit=0.5)
                    



