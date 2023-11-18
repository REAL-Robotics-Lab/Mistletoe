import moteus_pi3hat

def generate_transport():
    # can_cfg = moteus_pi3hat.CanConfiguration()
    # can_cfg.slow_bitrate = 1_000_000
    # can_cfg.fast_bitrate = 5_000_000
    # can_cfg.fdcan_frame = False
    # can_cfg.bitrate_switch = False
    # can_cfg.automatic_retransmission = True
    # can_cfg.restricted_mode = False
    # can_cfg.bus_monitor = False

    # # If buses are not listed, then they default to the parameters
    # # necessary to communicate with a moteus controller.
    # can_config = {
    #     1: can_cfg,
    #     2: can_cfg,
    #     3: can_cfg,
    #     4: can_cfg
    # }

    # Define servo to bus map
    servo_bus_map = {
        1 : [11, 12], 
        2 : [21, 22],
        3 : [31, 32],
        4 : [41, 42]
    }

    # Command Transport
    return moteus_pi3hat.Pi3HatRouter(
                                    # can=can_config,
                                    servo_bus_map=servo_bus_map)