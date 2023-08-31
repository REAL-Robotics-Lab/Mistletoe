import moteus
import time
import argparse
import asyncio

import MotorState 

parser = argparse.ArgumentParser(
    prog='Configure Motor',
    description='Load configuration file and configure motor'
)
parser.add_argument('id_hip', help='CAN ID of hip join motor', type=int)
parser.add_argument('id_knee', help='CAN ID of knee joint motor', type=int)
parser.add_argument('angle_hip', help='Angle of the hip motor', type=float)
parser.add_argument('angle_knee', help='Angle of the knee motor', type=float)
args = parser.parse_args()

async def main():
    transport = moteus.Fdcanusb()
    c1 = moteus.Controller(id=args.id_hip)
    c2 = moteus.Controller(id=args.id_knee)

    await transport.cycle([
      c1.make_position(position=0.5, query=False),
      c2.make_position(position=0.5, query=False),
    ])
    m1 =  MotorState()
    m2 =  MotorState()

    while True:
        states = await transport.cycle([
            c1.make_query(),
            c2.make_query(),
        ])

        m1.update(states[0])
        m2.update(states[1])

        print(f'Motor 1: \n{m1}')
        print(f'Motor 2: \n{m2}')

        time.sleep(0.05) # Do not spam moteus

asyncio.run(main())
