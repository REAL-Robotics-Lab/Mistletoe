import moteus
import time
import argparse
import asyncio

from motor_state import MotorState

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
controller1 = moteus.Controller(id=args.id_hip)
controller2 = moteus.Controller(id=args.id_knee)

async def main():

    motor1 =  MotorState()
    motor2 =  MotorState()

    while True:
        
        command1 = controller1.make_position(position=0.5, query=True, maximum_torque=1.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command2 = controller2.make_position(position=0.5, query=True, maximum_torque=1.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        
        states = await transport.cycle([
            command1,
            command2
        ])

        motor1.update(states[0])
        motor2.update(states[1])

        print(f'Motor 1: \n{motor1}')
        print(f'Motor 2: \n{motor2}')

        time.sleep(0.05) # Do not spam moteus

async def clean():
    await transport.cycle([controller1.make_stop()])
    await transport.cycle([controller2.make_stop()])

try:
    asyncio.run(main())
except KeyboardInterrupt:
    asyncio.run(clean())
