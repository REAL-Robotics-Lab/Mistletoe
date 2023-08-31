# Test motor configuration

import moteus
import asyncio
import argparse

from motor_state import MotorState

parser = argparse.ArgumentParser(
    prog='Configure Motor',
    description='Load configuration file and configure motor'
)
parser.add_argument('id', help='CAN ID', type=int)
args = parser.parse_args()

async def main():
    controller: moteus.Controller = moteus.Controller(id=args.id)
    motor: MotorState = MotorState()
    transport: moteus.Transport = moteus.get_singleton_transport()

    command: moteus.Command = controller.make_position(position=0, query=True, maximum_torque=1, velocity=5)
    await transport.cycle([command])

    while True:
        command = controller.make_query()
        states: [moteus.Command] = await transport.cycle([command])

        motor.update(states[0])

        print(motor)

asyncio.run(main())
