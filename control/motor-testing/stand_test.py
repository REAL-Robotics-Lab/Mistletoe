import moteus
import time
import argparse
import asyncio

from motor import *

transport = moteus.Fdcanusb(disable_brs=True)
front_right = Leg(4, 1, transport)
front_left = Leg(2, 3, transport)

async def main():
    # await front_right.update()
    # await front_left.update()
    # front_right.zero()
    # front_left.zero()
    await front_left.set_state(0, 0)

    while True:
        # await leg.update()
        # print(leg)
        await front_right.set_state(-1.5, 0.2)
        time.sleep(2)
        await front_right.set_state(1.5, -0.2)
        time.sleep(2)

async def clean():
   await front_right.stop()
   await front_left.stop()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    asyncio.run(clean())
