import moteus
import asyncio
import time
import argparse
import util

import sys
sys.path.append('../motor-testing')
sys.path.append('../gait')
import util
from trajectory import Trajectory

from motor_state import MotorState

util.confirm_operator_zeroed()

transport: moteus.Transport = util.generate_transport()

c11 = moteus.Controller(11, transport=transport)
c12 = moteus.Controller(12, transport=transport)

leg_center_dist_mm = 175.87
leg_center_dist_m = leg_center_dist_mm / 1000

swing_radius_m = 0.05

drag_time = 0.25
swing_time = 0.25
refresh_rate = 0.01
dist_to_ground = -0.25

trajectory = Trajectory(refresh_rate, leg_center_dist_m)
trajectory.set_half_circle(dist_to_ground, drag_time, swing_time, swing_radius=swing_radius_m)

async def main():
    # print('zeroing controllers...')

    # await util.zero_controller(controller=c11)
    # print('controller zeroed')
    # await util.zero_controller(controller=c12)
    # print('controller zeroed')

    print('starting position commands')


    while True:
        angles = trajectory.get_next_angles_revolutions()

        command11 = c11.make_position(position=angles[0], query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=20, accel_limit=10)
        command12 = c12.make_position(position=-1 * angles[1], query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=20, accel_limit=10)
        
        print(angles[0])
        print(-angles[1])

        states: [moteus.Command] = await transport.cycle([
            command11,
            command12,
        ])

        time.sleep(refresh_rate)

async def clean():
    await transport.cycle([c11.make_stop()])
    await transport.cycle([c12.make_stop()])

try:
    asyncio.run(main())
except Exception as error:
    print(error)
    asyncio.run(clean())
except KeyboardInterrupt:
    print('\nExit motor testing')
    asyncio.run(clean())

