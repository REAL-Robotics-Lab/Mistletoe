# Test file to test zeroing controllers

import moteus
import asyncio
import time
import argparse
import util

import sys
sys.path.append('../')
import util


# util.confirm_operator_zeroed()

transport = util.generate_transport()

controller = moteus.Controller(id=31,transport=transport)
stream = moteus.Stream(controller=controller)

async def main():
    # copied the do_set_offset method inside of moteus_tool code
    # encoding in latin1 allows to bypass concatination error
    await stream.drain()
    await stream.flush_read()
    print('das')
    await stream.command('d cfg-set-output 0'.encode('latin1'))
    await stream.flush_read()
    print('das')
    await stream.flush_read()
    await stream.command('conf write'.encode('latin1'))
    await stream.flush_read()
    print('das')
    await stream.command('d rezero 0'.encode('latin1'))
    await stream.flush_read()
    await stream.drain()
    print('das')

asyncio.run(main())