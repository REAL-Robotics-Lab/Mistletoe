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

    current_state: tuple[tuple[float, float], tuple[float, float]]

    def __init__(self, motor_manager, hip_motor_id, knee_motor_id, out_of_phase=False) -> None:
        self.motor_manager = motor_manager
        self.hip_motor_id = hip_motor_id
        self.knee_motor_id = knee_motor_id

        self.out_of_phase = out_of_phase

        self.hip_motor = motor_manager.get_motor(hip_motor_id)
        self.knee_motor = motor_manager.get_motor(knee_motor_id)
        self.trajectory = None
        self.next_trajectory = None
        self.current_state = None

    def update(self):
        print(self.hip_motor.get_status())
        print(self.knee_motor.get_status())
        if self.trajectory is None or self.trajectory.get_finished() == True:
            if self.next_trajectory != None:
                self.set_trajectory(self.next_trajectory)
        
        if self.trajectory is not None:
            self.set_leg_position()
        
    def set_trajectory(self, trajectory: Trajectory):
        if self.trajectory is None or self.trajectory.get_finished() == True:
            self.trajectory = trajectory
        else:
            self.next_trajectory = trajectory

    def set_leg_position(self):
        return
        if self.current_state is None or (self.hip_motor.at_desired_position() and self.knee_motor.at_desired_position()):
            self.trajectory.get_next_state()

            self.current_state = self.trajectory.get_next_state()
            angles, velocities = self.current_state

            self.hip_motor.set_position(position=(angles[0] % 1), target_velocity=velocities[0])
            self.knee_motor.set_position(position=(-1 * angles[1]) % 1, target_velocity=velocities[1])




