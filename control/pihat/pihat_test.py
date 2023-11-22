#!/usr/bin/python3

import asyncio
import moteus
import moteus_pi3hat
import time

async def main(refresh_rate: float):
    # The parameters of each CAN bus can be set at construction time.
    # The available fields can be found in the C++ header at
    # Pi3Hat::CanConfiguration
    # slow_bitrate : int
    # fast_bitrate : int
    # fdcan_frame : bool
    # bitrate_switch : bool
    # automatic_retransmission : bool
    # restricted_mode : bool
    # bus_monitor : bool
    # std_rate : CanRateOverride
    # fd_rate : CanRateOverride

    can_cfg = moteus_pi3hat.CanConfiguration()
    can_cfg.slow_bitrate = 1_000_000
    can_cfg.fast_bitrate = 5_000_000
    can_cfg.fdcan_frame = False
    can_cfg.bitrate_switch = False
    can_cfg.automatic_retransmission = True
    can_cfg.restricted_mode = False
    can_cfg.bus_monitor = False

    # If buses are not listed, then they default to the parameters
    # necessary to communicate with a moteus controller.
    can_config = {
        1: can_cfg,
        2: can_cfg,
        3: can_cfg,
        4: can_cfg
    }

    # Define servo to bus map
    servo_bus_map = {
        1 : [11, 12], 
        2 : [21, 22],
        3 : [31, 32],
        4 : [41, 42]
    }

    # Command Transport
    transport = moteus_pi3hat.Pi3HatRouter(can=can_config,
                                           servo_bus_map=servo_bus_map)

    controllers = []
    # Initialize Controllers
    for bus in servo_bus_map.keys():
        for id in servo_bus_map[bus]:
            controllers.append(moteus.Controller(id=id, transport=transport))

    cycle_delay: float = 1 / refresh_rate

    while True:
        messages = []

        # A single 'transport.cycle' call's message list can contain a
        # mix of "raw" frames and those generated from
        # 'moteus.Controller'.
        #
        # If you want to listen on a CAN bus without having sent a
        # command with 'reply_required' set, you can use the
        # 'force_can_check' optional parameter.  It is a 1-indexed
        # bitfield listing which additional CAN buses should be
        # listened to.

        results = await transport.cycle(
            messages, 
            force_can_check = (0b01111)
        )

        # If any raw CAN frames are present, the result list will be a
        # mix of moteus.Result elements and can.Message elements.
        # They each have the 'bus', 'arbitration_id', and 'data'
        # fields.
        #
        # moteus.Result elements additionally have an 'id' field which
        # is the moteus servo ID and a 'values' field which reports
        # the decoded response.
        for result in results:
            if hasattr(result, 'id'):
                # This is a moteus structure.
                print(f"{time.time():.3f} MOTEUS {result}")
            else:
                # This is a raw structure.
                print(f"{time.time():.3f} BUS {result.bus}  " +
                      f"ID {result.arbitration_id:x}  DATA {result.data.hex()}")

        await asyncio.sleep(cycle_delay)


if __name__ == '__main__':
    asyncio.run(main())