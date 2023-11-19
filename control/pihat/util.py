import moteus_pi3hat
import sys
import moteus

# This function should be added to the top of every quadruped script to confirm that the operator has zeroed the quadruped, until we bother to make a homing script.

def confirm_operator_zeroed():
    confirmation_msg = '''
==========================================\n
!!! IMPORTANT !!! \n 
Confirm that you have completed the homing sequence of the quadruped by typing: QUADRUPED ZEROED \n
==========================================\n
    '''
    confirmation = input(confirmation_msg)
    if confirmation.upper() == 'QUADRUPED ZEROED':
        print('Starting script')
    else:
        print('Confirmation failed')
        sys.exit()

# Generates a transport for the Pi3Hat for default quadruped BUS+ID configuration.

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

# copied the do_set_offset method inside of moteus_tool code
async def zero_controller(controller: moteus.Controller):
    stream = moteus.Stream(controller=controller)
    # flushing the read helps with problems that we encountered where it just stops 
    await stream.flush_read()
    await stream.command('d cfg-set-output 0'.encode('latin1'))
    await stream.flush_read()
    await stream.command('conf write'.encode('latin1'))
    await stream.flush_read()
    await stream.command('d rezero 0'.encode('latin1'))
    await stream.flush_read()
