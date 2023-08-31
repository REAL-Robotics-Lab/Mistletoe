# Test motor configuration

import moteus
import asyncio
import argparse

parser = argparse.ArgumentParser(
    prog='Configure Motor',
    description='Load configuration file and configure motor'
)
parser.add_argument('id', help='CAN ID', type=int)
args = parser.parse_args()

async def main():
    controller = moteus.Controller(id=args.id)

    while True:
        state = controller.make_query()

        print(f'Position: {state.data[moteus.Register.POSITION]}')
        print(f'Absolute Position : {state.data[moteus.Register.POSITION]}')

asyncio.run(main())
