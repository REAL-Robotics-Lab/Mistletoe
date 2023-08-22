import moteus
import time
import sched
import math
import asyncio

async def main():
    transport = moteus.Fdcanusb()
    c1 = moteus.Controller(id=0)
    c2 = moteus.Controller(id=1)

    await transport.cycle([
      c1.make_position(position=0.5, query=True),
      c2.make_position(position=0.5, query=True),
    ])

    while True:
        states = await transport.cycle([
            c1.make_query(),
            c2.make_query(),
        ])

        print('Controller 1:')
        print(f'Position: {states[0].values[moteus.Register.POSITION]}')
        print(f'Trajectory Complete: {states[0].values[moteus.Register.TRAJECTORY_COMPLETE]}')

        print('Controller 2:')
        print(f'Position: {states[1].values[moteus.Register.POSITION]}')
        print(f'Trajectory Complete: {states[1].values[moteus.Register.TRAJECTORY_COMPLETE]}')

asyncio.run(main())
