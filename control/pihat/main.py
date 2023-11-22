import asyncio
import time
from motor import MotorManager, Motor
import util
from leg import Leg
from trajectory import HalfCircleTrajectory, StandingTrajectory

motor_manager = MotorManager(motor_ids=[11,12,21,22,31,32,41,42])


async def main():
    leg = Leg(motor_manager, 11, 12)

    leg_center_dist_mm = 175.87
    leg_center_dist = leg_center_dist_mm / 1000
    swing_radius_m = 0.05
    dist_to_ground = -0.25

    running_trajectory = HalfCircleTrajectory(50, leg_center_dist, dist_to_ground, swing_radius_m, 0.5)
    standing_trajectory = StandingTrajectory(leg_center_dist, dist_to_ground)

    while True:
        leg.update()
        motor_manager.update()
        leg.set_trajectory(running_trajectory)
        leg.set_trajectory(standing_trajectory)
        time.sleep(0.01)

async def clean():
    motor_manager.stop_motors()

try:
    asyncio.run(main())
except Exception as error:
    print(error)
    asyncio.run(clean())
except KeyboardInterrupt:
    print('\nExit motor testing')
    asyncio.run(clean())