import asyncio
import time
from motor import MotorManager
from leg import Leg
from trajectory import HalfCircleTrajectory, StandingTrajectory
from threading import Thread
import traceback

from atexit import register

motor_manager = MotorManager(motor_ids=[11,12,21,22,31,32,41,42], min_voltage=22.25)

leg1 = Leg(motor_manager, 11, 12, hip_inverted=False, knee_inverted=False, hip_offset=0, knee_offset=-0)
leg2 = Leg(motor_manager, 21, 22, hip_inverted=True, knee_inverted=True, hip_offset=0, knee_offset=0)
leg3 = Leg(motor_manager, 31, 32, hip_inverted=False, knee_inverted=False, hip_offset=0, knee_offset=0)
leg4 = Leg(motor_manager, 41, 42, hip_inverted=True, knee_inverted= True, hip_offset=0, knee_offset=0)

initialization_complete = False
program_active = True

async def leg_control(frequency: float=200):
    global program_active

    base_time = time.perf_counter()

    period = 1/frequency

    curr_period = period

    while program_active:
        current_time = time.perf_counter()
        curr_period = current_time - base_time
        
        if curr_period >= period:
            # print(f"Period: {curr_period:.5f}")
            leg1.update()
            leg2.update()
            leg3.update()
            leg4.update()
            await motor_manager.update()

            # Update DT
            base_time = current_time

def control_leg_async():
    asyncio.run(leg_control())

def control():
    global initialization_complete
    global program_active
    print("Initializing...")

    # offset values were found at laying down position
    leg_center_dist_mm = 175.87
    leg_center_dist = leg_center_dist_mm / 1000
    swing_radius_m = 0.05
    dist_to_ground = -0.275

    print("Initializing Running Trajectory: ")

    running_trajectory = HalfCircleTrajectory(filepath='half_circle_traj.csv')

    print("Initializing Standing Trajectory: ")

    standing_trajectory = StandingTrajectory(leg_center_dist, dist_to_ground, filepath="standing_traj.csv")
    
    # print("Initializing Running Trajectory: ")
    
    # running_trajectory = HalfCircleTrajectory(num_setpoints=100, leg_center_distance=leg_center_dist, dist_to_ground=dist_to_ground, swing_radius=swing_radius_m)
    # running_trajectory.save_trajectory('half_circle_traj.csv')

    # leg1.set_trajectory(running_trajectory, offset=0)
    # leg2.set_trajectory(running_trajectory, offset=0.5)
    # leg3.set_trajectory(running_trajectory, offset=0,  reversed=True)
    # leg4.set_trajectory(running_trajectory, offset=0.5, reversed=True)

    leg1.set_trajectory(standing_trajectory)
    leg2.set_trajectory(standing_trajectory)
    leg3.set_trajectory(standing_trajectory)
    leg4.set_trajectory(standing_trajectory)

    print("Initialization complete!")
    initialization_complete = True

    # Input Loop
    user_input = ""
    while not user_input.lower().startswith(("exit")):
        user_input = input("Input: ").lower()
        if "stand" in user_input:
            leg1.set_trajectory(standing_trajectory)
            leg2.set_trajectory(standing_trajectory)
            leg3.set_trajectory(standing_trajectory)
            leg4.set_trajectory(standing_trajectory)
            print("Current state: standing")
        elif "walk" in user_input:
            leg1.set_trajectory(running_trajectory, offset=0)
            leg2.set_trajectory(running_trajectory, offset=0.5)
            leg3.set_trajectory(running_trajectory, offset=0,  reversed=True)
            leg4.set_trajectory(running_trajectory, offset=0.5, reversed=True)
            print("Current state: walking")
    program_active = False

async def clean():
    global program_active
    program_active = False
    time.sleep(0.1)
    await motor_manager.stop_motors()

def main():
    leg_thread = Thread(target=control_leg_async)
    control_thread = Thread(target=control)
    try:
        control_thread.start()

        while not initialization_complete:
            time.sleep(0.5)
        
        time.sleep(0.1)
        leg_thread.start()

        while control_thread.is_alive():
            time.sleep(0.1)
        
        print("Stopping...")
        asyncio.run(clean())
        
    except Exception as error:
        print(traceback.format_exc())
        asyncio.run(clean())
    except KeyboardInterrupt:
        print('\nExit motor testing')
        asyncio.run(clean())

if __name__ == '__main__':
    main()