# Test motor configuration

import moteus
import asyncio
import time
import argparse

from motor_state import MotorState

parser = argparse.ArgumentParser(
    prog='Configure Motor',
    description='Load configuration file and configure motor'
)
parser.add_argument('id', help='CAN ID', type=int)
parser.add_argument('angle', help='Angle to set the motor to', type=float)
args = parser.parse_args()
controller: moteus.Controller = moteus.Controller(id=args.id)
motor: MotorState = MotorState()
transport: moteus.Transport = moteus.get_singleton_transport()

async def main():
    while True:
        command = controller.make_position(position=None, stop_position=args.angle / 360,query=True, maximum_torque=1, velocity=0.1,watchdog_timeout=None)
        states: [moteus.Command] = await transport.cycle([command])

        motor.update(states[0])

        print(motor)

        time.sleep(0.05)

async def clean():
    await transport.cycle([controller.make_stop()])

try:
    asyncio.run(main())
except KeyboardInterrupt:
    asyncio.run(clean())
