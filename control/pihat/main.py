import asyncio
import time
from motor import MotorManager, Motor
import util
from leg import Leg
from trajectory import HalfCircleTrajectory, StandingTrajectory
import threading
import traceback
motor_manager = MotorManager(motor_ids=[11,12,21,22,31,32,41,42], min_voltage=22.25)

leg1 = Leg(motor_manager, 11, 12, hip_inverted=False, knee_inverted=False, hip_offset=0, knee_offset=-0)
leg2 = Leg(motor_manager, 21, 22, hip_inverted=True, knee_inverted=True, hip_offset=0, knee_offset=0)
leg3 = Leg(motor_manager, 31, 32, hip_inverted=False, knee_inverted=False, hip_offset=0, knee_offset=0)
leg4 = Leg(motor_manager, 41, 42, hip_inverted=True, knee_inverted= True, hip_offset=0, knee_offset=0)

async def main():
    # offset values were found at laying down position

    leg_center_dist_mm = 175.87
    leg_center_dist = leg_center_dist_mm / 1000
    swing_radius_m = 0.05
    dist_to_ground = -0.275
    running_trajectory = HalfCircleTrajectory(filepath='half_circle_traj.csv')
    # running_trajectory = HalfCircleTrajectory(num_setpoints=100, leg_center_distance=leg_center_dist, dist_to_ground=dist_to_ground, swing_radius=swing_radius_m)
    # running_trajectory.save_trajectory('half_circle_traj.csv')
    # standing_trajectory = StandingTrajectory(leg_center_dist, dist_to_ground)
    # standing_trajectory = StandingTrajectory(leg_center_dist, dist_to_ground)

    leg1.set_trajectory(running_trajectory, offset=0)
    leg2.set_trajectory(running_trajectory, offset=0.5)
    leg3.set_trajectory(running_trajectory, offset=0,  reversed=True)
    leg4.set_trajectory(running_trajectory, offset=0.5, reversed=True)

    # leg1.set_trajectory(standing_trajectory)
    # leg2.set_trajectory(standing_trajectory)
    # leg3.set_trajectory(standing_trajectory)
    # leg4.set_trajectory(standing_trajectory)

    base_time = time.time()
    frequency = 1/200
    while True:
        current_time = time.time()
        if current_time - base_time >= frequency:
            leg1.update()
            leg2.update()
            leg3.update()
            leg4.update()
            await motor_manager.update()

            # Update DT
            base_time = current_time

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