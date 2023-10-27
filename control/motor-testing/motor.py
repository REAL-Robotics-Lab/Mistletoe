import moteus
from typing import Dict, Any
import asyncio

class Motor:
    _position: float
    offset: float
    controller: moteus.Controller
    transport: moteus.Fdcanusb
    
    def __init__(self, controller, transport: moteus.Fdcanusb, offset=0) -> None:
        self.controller = controller
        self.offset = offset
        self._position = 0
        self.transport = transport

    def update_status(self, state: Dict) -> None:
        self._position = state.values[moteus.Register.POSITION]
    
    def zero_position(self) -> None:
        self.offset = self._position
    
    def make_query(self) -> moteus.Command:
        return self.controller.make_query()
    
    async def set_position(self, position: float, velocity: float) -> None:
        await self.send_command(f'd pos {position+self.offset} 0 9 v{velocity} a4')
    
    async def stop(self) -> None:
        await self.send_command('d stop')

    def get_position(self) -> float:
        return self._position - self.offset

    def set_offset(self, offset) -> float:
        self.offset = offset
    
    def get_original_position(self) -> float:
        return self._position
    
    async def send_command(self, cmd: str) -> None:
        await self.transport.write(self.controller.make_diagnostic_write(f'\r\n{cmd}\r\n'.encode('latin1')))
        await self.transport.write(self.controller.make_diagnostic_read())

    def __repr__(self) -> str:
        return f'Position: {self.get_original_position()}, Zeroed Position: {self.get_position()}'


class Leg:

    hip_motor: Motor
    knee_motor: Motor
    transport: moteus.Fdcanusb

    def __init__(self, hip_id: int, knee_id: int, transport: moteus.Fdcanusb) -> None:
        self.hip_motor = Motor(moteus.Controller(id=hip_id), transport)
        self.knee_motor = Motor(moteus.Controller(id=knee_id), transport)
        self.transport = transport

    async def update(self):
        states = await self.transport.cycle([
            self.hip_motor.make_query(), self.knee_motor.make_query()
        ])
        self.hip_motor.update_status(states[0])
        self.knee_motor.update_status(states[1])

    def zero(self):
        self.hip_motor.zero_position()
        self.knee_motor.zero_position()

    async def set_state(self, hip_pos: float, knee_pos: float):
        await self.hip_motor.set_position(hip_pos, 0.01)
        await self.knee_motor.set_position(knee_pos, 0.01)

    async def stop(self):
        await self.hip_motor.stop()
        await self.knee_motor.stop()
    
    def __repr__(self) -> str:
        return f'Hip: {self.hip_motor}\nknee: {self.knee_motor}'
