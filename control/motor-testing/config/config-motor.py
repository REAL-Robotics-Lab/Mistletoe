# Load configuration file and configure motor

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

c1 = moteus.Controller(id=args.id)
stream = moteus.Stream(controller=c1)

async def load_config_file():
    with open(args.filename, 'r') as motor_config:
        lines = [line.strip() for line in motor_config.readlines()]
        for line in lines:
            result = await stream.command(line.encode('latin1'))
            print(result)

asyncio.run(load_config_file())
