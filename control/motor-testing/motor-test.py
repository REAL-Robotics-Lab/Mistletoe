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
    controller: moteus.Controller = moteus.Controller(id=args.id)
    transport: moteus.Transport = moteus.get_singleton_transport()

    command: moteus.Command = controller.make_position(position=0, query=True, maximum_torque=1, velocity=5)
    while True:
        command = controller.make_query()
        results: [moteus.Command] = await transport.cycle([command])

        # print(f'Position: {state.data[moteus.Register.POSITION]}')
        # print(f'Absolute Position : {state.data[moteus.Register.ABS_POSITION]}')
        print(f'Data: {results[0].values[moteus.Register.POSITION]}')


asyncio.run(main())
