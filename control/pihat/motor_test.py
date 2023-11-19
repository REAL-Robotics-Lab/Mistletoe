# Test motor configuration

import moteus
import asyncio
import time
import argparse
import util

import sys
sys.path.append('../motor-testing')
import util

from motor_state import MotorState

util.confirm_operator_zeroed()

transport: moteus.Transport = util.generate_transport()

c11 = moteus.Controller(11, transport=transport)
c12 = moteus.Controller(12, transport=transport)
c21 = moteus.Controller(21, transport=transport)
c22 = moteus.Controller(22, transport=transport)
c31 = moteus.Controller(31, transport=transport)
c32 = moteus.Controller(32, transport=transport)
c41 = moteus.Controller(41, transport=transport)
c42 = moteus.Controller(42, transport=transport)

motor_state_11 = MotorState()
motor_state_12 = MotorState()
motor_state_21 = MotorState()
motor_state_22 = MotorState() 
motor_state_31 = MotorState()
motor_state_32 = MotorState(offset = 0)
motor_state_41 = MotorState()
motor_state_42 = MotorState(offset = 0)

async def main():
    print('zeroing controllers...')

    await util.zero_controller(controller=c11)
    print('controller zeroed')
    await util.zero_controller(controller=c12)
    print('controller zeroed')
    await util.zero_controller(controller=c21)
    print('controller zeroed')
    await util.zero_controller(controller=c22)
    print('controller zeroed')
    await util.zero_controller(controller=c31)
    print('controller zeroed')
    await util.zero_controller(controller=c32)
    print('controller zeroed')
    await util.zero_controller(controller=c41)
    print('controller zeroed')
    await util.zero_controller(controller=c42)
    print('controller zeroed')

    print('starting position commands')

    while True:
        command11 = c11.make_position(position=0.125, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command12 = c12.make_position(position=-0.65, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command21 = c21.make_position(position=-0.125, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command22 = c22.make_position(position=0.65, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command31 = c31.make_position(position=-0.125, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command32 = c32.make_position(position=0.65, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command41 = c41.make_position(position=0.125, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        command42 = c42.make_position(position=-0.65, query=True, maximum_torque=4.0, velocity=0.0, velocity_limit=0.5, accel_limit=2.0)
        
        states: [moteus.Command] = await transport.cycle([
            command11,
            command12,
            command21,
            command22,
            command31,
            command32,
            command41,
            command42,
        ])

        motor_state_11.update(states[0])
        motor_state_12.update(states[1])
        motor_state_21.update(states[2])
        motor_state_22.update(states[3])
        motor_state_31.update(states[4])
        motor_state_32.update(states[5])
        motor_state_41.update(states[6])
        motor_state_42.update(states[7])

        # print(f'Motor 1: \n{motor_state_11}')
        # print(f'Motor 2: \n{motor_state_12}')
        # print(f'Motor 3: \n{motor_state_21}')
        # # print(f'Motor 4: \n{motor_state_22}')
        # print(f'Motor 5: \n{motor_state_31}')
        # # print(f'Motor 6: \n{motor_state_32}')
        # print(f'Motor 7: \n{motor_state_41}')
        # # print(f'Motor 8: \n{motor_state_42}')

        time.sleep(0.05)

async def clean():
    await transport.cycle([c11.make_stop()])
    await transport.cycle([c12.make_stop()])
    await transport.cycle([c21.make_stop()])
    await transport.cycle([c22.make_stop()])
    await transport.cycle([c31.make_stop()])
    await transport.cycle([c32.make_stop()])
    await transport.cycle([c41.make_stop()])
    await transport.cycle([c42.make_stop()])

try:
    asyncio.run(main())
except Exception as error:
    print(error)
    asyncio.run(clean())
except KeyboardInterrupt:
    print('\nExit motor testing')
    asyncio.run(clean())

