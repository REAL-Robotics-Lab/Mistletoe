import moteus
import util
from enum import Enum
# from typing import TypeAlias

# required for changing resolution
from moteus import multiplex as mp

class ControlMode(Enum):
    POSITION_CONTROL = 1
    STOP = 2

# rip 3.9

# Revolutions: TypeAlias = float
# RPS: TypeAlias = float


class Motor:
    controller: moteus.Controller
    current_command: moteus.Command

    status: dict

    desired_position: float
    position: float
    position_tolerance: float
    velocity: float
    max_torque: float
    max_velocity: float
    max_accel: float
    transport: moteus.Transport

    voltage: float
    min_voltage: float
    voltage_checked: bool

    id: int

    control_mode: ControlMode

    inverted: bool
    offset: float

    def __init__(
        self,
        id: int,
        transport: moteus.Transport,
        position_tolerance: float = 0.05,
        max_torque: float = 4.0,
        max_velocity: float = 0.5,
        max_accel: float = 2.0,
        min_voltage: float = 22.5 # 6S minimum voltage
    ):
        # set the query resolution of controller voltage to be INT16 for higher resolution
        query_resolution = moteus.QueryResolution()
        query_resolution.voltage = mp.INT32

        self.controller = moteus.Controller(id, transport=transport, query_resolution=query_resolution)
        self.position_tolerance = position_tolerance
        self.max_torque = max_torque
        self.max_velocity = max_velocity
        self.max_accel = max_accel

        self.inverted = False
        self.offset = 0

        self.current_command = self.controller.make_query()
        self.control_mode = ControlMode.STOP
        self.desired_position = 0
        self.position = 0
        self.position_tolerance = position_tolerance
        self.velocity = 0
        self.max_torque = max_torque
        self.max_velocity = max_velocity
        self.max_accel = max_accel
        self.id = id
        self.min_voltage = min_voltage
        self.voltage_checked = False

        self.transport = transport

    def update_status(self, status) -> None:
        if self.control_mode == ControlMode.POSITION_CONTROL:
            pass
        elif self.control_mode == ControlMode.STOP:
            pass

        self.status = status
        self.position = status.values[moteus.Register.POSITION]
        self.velocity = status.values[moteus.Register.VELOCITY]
        self.voltage = status.values[moteus.Register.VOLTAGE]

        if self.voltage_checked == False and self.voltage <= self.min_voltage:
            raise VoltageTooLowException(voltage=self.voltage, controller_id=self.id)
        
        self.voltage_checked = True
        
    def get_status(self) -> str:
        return f"Motor {self.id}: Pos: {self.position}, Velocity: {self.velocity}, Desired Pos: {self.desired_position}"

    def set_position(
        self,
        position,
        velocity=0,
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

        # Invert position given if inverted
        if self.inverted == True:
            position = -1 * position

        # add offset to position
        position -= self.offset

        # Update desired position and control mode
        self.desired_position = position
        
        # print(f'desired position: {self.desired_position}')
        # print(f'real position: {self.position}')
        
        self.control_mode = ControlMode.POSITION_CONTROL

        # print(f"making position ({self.id}): {position}, {velocity}")

        # Set current command to position control
        self.current_command = self.controller.make_position(
            position=position,
            velocity=velocity,
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

    # TODO: Realistically should call one last update cycle in the clean() method in the main file to ensure that make_stop command is being sent
    async def stop(self):
        # self.current_command = self.controller.make_stop()
        # print(self.transport)
        # await self.controller.set_stop()
        await self.transport.cycle([self.controller.make_stop()])
        # print('controller stopped')

    def get_current_command(self) -> moteus.Command:
        return self.current_command

    def at_desired_position(self) -> bool:
        print(f"Motor {self.id} Distance from desired position: {abs(self.position - self.desired_position)}, Tolerance: {self.position_tolerance}, Real position: {self.position}, Desired Position: {self.desired_position}")
        return abs(self.position - self.desired_position) < self.position_tolerance

    def get_position(self) -> float:
        return self.position

    def get_velocity(self) -> float:
        return self.velocity

    def set_inverted(self, inverted: bool) -> None:
        self.inverted = inverted

    def set_offset(self, offset: float) -> None:
        self.offset = offset



""" Ensures that motors are cycled and have their statuses updated.
    Run update() once per cycle.
"""

class MotorManager:
    transport: moteus.Transport
    motors: dict[int, Motor]

    def __init__(self, motor_ids: list[int], transport: moteus.Transport = None, min_voltage: float = 22.5):
        if transport == None:
            self.transport = util.generate_transport()
        self.motors = {id: Motor(id, self.transport, min_voltage=min_voltage) for id in motor_ids}

    def get_motor(self, id: int):
        try:
            return self.motors[id]
        except KeyError:
            print(f"Error: Motor #{id} not found.")
            return None

    async def stop_motors(self):
        for motor in self.motors.values():
            await motor.stop()

    async def update(self):
        # Cycle the motors
        
        statuses = await self.transport.cycle(
            [motor.get_current_command() for motor in self.motors.values()]
        )

        # Update the statuses
        for idx, motor in enumerate(self.motors.values()):
            motor.update_status(statuses[idx])

class VoltageTooLowException(Exception):
    """Exception raised when voltage of system is below minimum threshold.
    """

    def __init__(self, voltage, controller_id) -> None:
        self.voltage = voltage
        self.controller_id = controller_id
        self.message = f'Voltage of system under minimum threshold, Voltage: {self.voltage} on ID: {self.controller_id}'
        super().__init__(self.message)