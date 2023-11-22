import moteus
import util
from enum import Enum
from typing import TypeAlias


class ControlMode(Enum):
    POSITION_CONTROL = 1
    STOP = 2


Revolutions: TypeAlias = float
RPS: TypeAlias = float


class Motor:
    controller: moteus.Controller
    current_command: moteus.Command

    status: dict

    desired_position: Revolutions
    position: Revolutions
    position_tolerance: Revolutions
    velocity: RPS
    max_torque: float
    max_velocity: float
    max_accel: float

    control_mode: ControlMode

    def update_status(self, status) -> None:
        if self.control_mode == ControlMode.POSITION_CONTROL:
            pass
        elif self.control_mode == ControlMode.STOP:
            pass

        self.status = status[moteus.Register.POSITION]
        self.position = status[moteus.Register.VELOCITY]
        self.desired_position = 0
        self.position = 0
        self.position_tolerance = 0
        self.velocity = 0
        self.max_torque = 0
        self.max_velocity = 0
        self.max_accel = 0
        self.control_mode = ControlMode.STOP

    def __init__(
        self,
        id: int,
        transport: moteus.Transport,
        position_tolerance: Revolutions = 0.01,
        max_torque: float = 4.0,
        max_velocity: float = 0.5,
        max_accel: float = 2.0,
    ):
        self.controller = moteus.Controller(id, transport=transport)
        self.position_tolerance = position_tolerance
        self.max_torque = max_torque
        self.max_velocity = max_velocity
        self.max_accel = max_accel

    def set_position(
        self,
        position,
        target_velocity=0,
        feedforward_torque=None,
        kp_scale=None,
        kd_scale=None,
        maximum_torque=None,
        stop_position=None,
        watchdog_timeout=None,
        velocity_limit=None,
        accel_limit=None,
        fixed_voltage_override=None,
    ) -> None:
        # Update the max torque, velocity, and accel if provided
        if maximum_torque:
            self.max_torque = maximum_torque
        if velocity_limit:
            self.max_velocity = velocity_limit
        if accel_limit:
            self.max_accel = accel_limit

        # Update desired position and control mode
        self.desired_position = position
        self.control_mode = ControlMode.POSITION_CONTROL

        # Set current command to position control
        self.current_command = self.controller.make_position(
            position=position,
            velocity=target_velocity,
            feedforward_torque=feedforward_torque,
            kp_scale=kp_scale,
            kd_scale=kd_scale,
            maximum_torque=self.max_torque,
            stop_position=stop_position,
            watchdog_timeout=watchdog_timeout,
            velocity_limit=self.max_velocity,
            accel_limit=self.max_accel,
            fixed_voltage_override=fixed_voltage_override,
            query=True,
        )

    def stop(self):
        self.current_command = self.controller.make_stop
        self.controller.set_stop()

    def get_current_command(self) -> moteus.Command:
        return self.current_command

    def at_desired_position(self) -> bool:
        return abs(self.position - self.desired_position) < self.position_tolerance

    def get_position(self) -> Revolutions:
        return self.position

    def get_velocity(self) -> Revolutions:
        return self.velocity


""" Ensures that motors are cycled and have their statuses updated.
    Run update() once per cycle.
"""

class MotorManager:
    transport: moteus.Transport
    motors: dict[int, Motor]

    def __init__(self, motor_ids: list[int], transport: moteus.Transport = None):
        if transport == None:
            self.transport = util.generate_transport()
        self.motors = {id: Motor(id, transport) for id in motor_ids}

    def get_motor(self, id: int):
        try:
            return self.motors[id]
        except KeyError:
            print(f"Error: Motor #{id} not found.")
            return None

    def stop_motors(self):
        for motor in self.motors.values():
            motor.stop()

    def update(self):
        # Cycle the motors
        statuses = self.transport.cycle(
            [motor.get_command() for motor in self.motors.values()]
        )

        # Update the statuses
        for idx, motor in enumerate(self.motors.values()):
            motor.update_status(statuses[idx])
