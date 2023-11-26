import asyncio
import time
from motor import MotorManager, Motor
import util
from leg import Leg
from trajectory import HalfCircleTrajectory, StandingTrajectory
import traceback
motor_manager = MotorManager(motor_ids=[11,12,21,22,31,32,41,42], min_voltage=22.5)


async def main():
    leg1 = Leg(motor_manager, 11, 12, hip_inverted=True, knee_inverted=True)
    # leg2 = Leg(motor_manager, 21, 22)
    # leg3 = Leg(motor_manager, 31, 32)
    # leg4 = Leg(motor_manager, 41, 42)

    leg_center_dist_mm = 175.87
    leg_center_dist = leg_center_dist_mm / 1000
    swing_radius_m = 0.05
    dist_to_ground = -0.25

    running_trajectory = HalfCircleTrajectory(50, leg_center_dist, dist_to_ground, swing_radius_m, -0)
    standing_trajectory = StandingTrajectory(leg_center_dist, dist_to_ground)

    while True:
        leg1.set_trajectory(standing_trajectory)
        # leg2.set_trajectory(standing_trajectory)
        # leg3.set_trajectory(standing_trajectory)
        # leg4.set_trajectory(standing_trajectory)

        leg1.update()
        # leg2.update()
        # leg3.update()
        # leg4.update()
        await motor_manager.update()
        time.sleep(0.01)

async def clean():
    await motor_manager.stop_motors()

try:
    asyncio.run(main())
except Exception as error:
    print(traceback.format_exc())
    asyncio.run(clean())
except KeyboardInterrupt:
    print('\nExit motor testing')
    asyncio.run(clean())