import moteus
import time
import argparse
import asyncio

from motor import Motor

transport = moteus.Fdcanusb(disable_brs=True)
motor1 = moteus.Controller(id=1)
motor2 = moteus.Controller(id=4)

async def main():
    start_time = time.time()
    # while time.time() - start_time < 4:
    #     command1 = motor1.make_position(position=args.angle_hip/360, maximum_torque=9, velocity=0.0, velocity_limit=0.05, accel_limit=2.0)
        
    #     states = await transport.cycle([
    #         command1
    #     ])

    #     motor1.update_status(states[0])
    #     print(f'Motor 1: \n{motor1}')

    #     time.sleep(0.05)
    # command = motor2.make_position(position=0.5, velocity=0.0, maximum_torque=1.0, velocity_limit=0.5, accel_limit=2.0)
    # await transport.cycle([command])

    # command1 = motor1.make_position(position=args.angle_hip, maximum_torque=1, velocity=0.0, velocity_limit=0.5, accel_limit=2)
    # command2 = motor2.make_position(position=args.angle_knee, maximum_torque=1, velocity=0.0, velocity_limit=0.5, accel_limit=2)
    # states = await transport.cycle([
    #     command1,
    #     command2
    # ])
    # print(f'Motor 1: \n{motor1}')
    # print(f'Motor 2: \n{motor2}')

    await transport.write(motor1.make_diagnostic_write('\r\nd pos 0 0 9 v0.5 a2\r\n'.encode('latin1')))
    await transport.write( motor1.make_diagnostic_read())
    await transport.write(motor2.make_diagnostic_write('\r\nd pos 0.5 0 9 v0.5 a2\r\n'.encode('latin1')))
    await transport.write(motor2.make_diagnostic_read())

    while True:
        pass

    # time.sleep (2)
    # await transport.cycle([motor1.make_stop(), motor2.make_stop()])

    # while True:
    #     # command1 = motor1.make_position(position=args.angle_hip, maximum_torque=1, velocity=0.0, velocity_limit=0.05, accel_limit=2)
    #     # command2 = motor2.make_position(position=args.angle_knee, maximum_torque=1, velocity=0.0, velocity_limit=0.05, accel_limit=2)
    

    #     # command1 = motor1.make_query()
    #     # command2 = motor2.make_query()

    #     # states = await transport.cycle([
    #     #     command1,
    #     #     command2
    #     # ])

    #     # motor1.update_status(states[0])
    #     # motor2.update_status(states[1])

    #     print(f'Motor 1: \n{motor1}')
    #     print(f'Motor 2: \n{motor2}')

    #     time.sleep(0.1) # Do not spam moteus

async def clean():
    # await transport.cycle([motor1.make_stop()])
    # await transport.cycle([motor2.make_stop()])
    await transport.write(motor1.make_diagnostic_write('d stop\r\n'.encode('latin1')))
    await transport.write(motor1.make_diagnostic_read())
    await transport.write(motor2.make_diagnostic_write('d stop\r\n'.encode('latin1')))
    await transport.write(motor2.make_diagnostic_read())

try:
    asyncio.run(main())
except KeyboardInterrupt:
    asyncio.run(clean())
