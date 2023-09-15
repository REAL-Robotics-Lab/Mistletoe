import moteus
import time
import argparse
import asyncio

from motor import Motor

parser = argparse.ArgumentParser(
    prog='Test Motor',
    description='Set the position for multiple motors given ID and angle'
)
parser.add_argument('id_hip', help='CAN ID of hip join motor', type=int)
parser.add_argument('id_knee', help='CAN ID of knee joint motor', type=int)
parser.add_argument('angle_hip', help='Angle of the hip motor', type=float)
parser.add_argument('angle_knee', help='Angle of the knee motor', type=float)
args = parser.parse_args()
transport = moteus.Fdcanusb()
motor1 = Motor(moteus.Controller(id=args.id_hip))
motor2 = Motor(moteus.Controller(id=args.id_knee))

async def main():
    while True:
        command1 = motor1.make_position(position=args.angle_hip/360, maximum_torque=1.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command2 = motor1.make_position(position=args.angle_knee/360, maximum_torque=1.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        
        states = await transport.cycle([
            command1,
            command2
        ])

        motor1.update_status(states[0])
        motor2.update_status(states[1])

        print(f'Motor 1: \n{motor1}')
        print(f'Motor 2: \n{motor2}')

        time.sleep(0.05) # Do not spam moteus

async def clean():
    await transport.cycle([motor1.make_stop()])
    await transport.cycle([motor2.make_stop()])

try:
    asyncio.run(main())
except KeyboardInterrupt:
    asyncio.run(clean())
