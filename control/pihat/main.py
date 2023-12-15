import asyncio
import time
from motor import MotorManager, Motor
import util
from leg import Leg
from trajectory import HalfCircleTrajectory, StandingTrajectory
import threading
import traceback
motor_manager = MotorManager(motor_ids=[11,12,21,22,31,32,41,42], min_voltage=22.5)

leg1 = Leg(motor_manager, 11, 12, hip_inverted=True, knee_inverted=True, hip_offset=0, knee_offset=-0)


async def main():
    # offset values were found at laying down position
    # leg2 = Leg(motor_manager, 21, 22, hip_inverted=False, knee_inverted=False, hip_offset=-0.2254791259765625, knee_offset=0.4503173828125)
    # leg3 = Leg(motor_manager, 31, 32, hip_inverted=False, knee_inverted=False, hip_offset=-0.22308349609375, knee_offset=0.4444732666015625)
    # leg4 = Leg(motor_manager, 41, 42, hip_inverted=True, knee_inverted= True, hip_offset=0.232330322265625, knee_offset=-0.44049072265625)

    # standing_trajectory = StandingTrajectory(leg_center_dist, dist_to_ground)

    while True:
        # leg2.update()
        # leg3.update()
        # leg4.update()
        await motor_manager.update()
        time.sleep(0.01)

async def clean():
    await motor_manager.stop_motors()

def compute_logic():
    leg_center_dist_mm = 175.87
    leg_center_dist = leg_center_dist_mm / 1000
    swing_radius_m = 0.05
    dist_to_ground = -0.275
    running_trajectory = HalfCircleTrajectory(50, leg_center_dist, dist_to_ground, swing_radius_m, uniform_velocity=0)
    while True:
        leg1.set_trajectory(running_trajectory)
        leg1.update()

        time.sleep(0.01)

logic_thread = threading.Thread(target=compute_logic)
logic_thread.start()

try:
    asyncio.run(main())
except Exception as error:
    print(traceback.format_exc())
    asyncio.run(clean())
except KeyboardInterrupt:
    print('\nExit motor testing')
    asyncio.run(clean())