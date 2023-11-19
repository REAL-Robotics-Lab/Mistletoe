# Load configuration file and configure motor

import sys
sys.path.append('../pihat')
import util

import moteus
import asyncio
import argparse

parser = argparse.ArgumentParser(
    prog='Configure Motor',
    description='Load configuration file and configure motor'
)
parser.add_argument('filename', help='Configuration file path', type=str)
parser.add_argument('id', help='CAN ID', type=int)
args = parser.parse_args()

transport = util.generate_transport()

c1 = moteus.Controller(id=args.id,transport=transport)
stream = moteus.Stream(controller=c1)

async def load_config_file():
    with open(args.filename, 'r') as motor_config:
        lines = [line.strip() for line in motor_config.readlines()]
        for num, line in enumerate(lines):
            try:
                result = await stream.command(line.encode('latin1'))
                await transport.write(c1.make_diagnostic_read())
                print(f"Success for option #{num} ({line}): {result}")
            except:
                print(f"Failure for option #{num} ({line})")
            

asyncio.run(load_config_file())
