import tinyik
import math
import numpy as np
import matplotlib.pyplot as plt

# TODO: maybe refractor so that trajectory is a abstract class and the specific trajectory extends from it and the trajectory generator method is an overridden abstract method

class Trajectory:
    def __init__(self, refresh_rate, leg_center_distance, out_of_phase = False) -> None:
        self.refresh_rate = refresh_rate
        self.leg_center_distance = leg_center_distance 
        self.leg = tinyik.Actuator(['z', [leg_center_distance, 0., 0.], 'z', [leg_center_distance, 0., 0.]])
        
        self.out_of_phase = out_of_phase

        self.counter = 0
        
        self.trajectory_pos = None
        self.trajectory_angles = None

    def generate_half_circle(self, dist_to_ground, drag_time, swing_time, swing_radius):
        trajectory_pos_x = 0
        trajectory_pos_y = dist_to_ground # init @ dist to ground

        self.leg.ee = [trajectory_pos_x, trajectory_pos_y, 0]
        
        drag_steps = int(drag_time/self.refresh_rate)
        swing_steps = int(swing_time/self.refresh_rate)
        total_steps = drag_steps + swing_steps

        angle_per_step = math.pi/swing_steps
        theta = 0 

        trajectory_angles = []
        trajectory_pos = [[],[]]


        # if a leg is out of phase it should stay in position until the other leg is at the top of the semicircle

        if self.out_of_phase == True:
            # lowk maybe shouldn't int but wtv
            for i in range(int(drag_steps/2 + total_steps/2)):
                trajectory_pos[0].append(trajectory_pos_x)
                trajectory_pos[1].append(trajectory_pos_y)
                trajectory_angles.append(self.leg.angles)

        for step_counter in range(total_steps):      
            if step_counter < drag_steps/2 or step_counter > drag_steps/2 + swing_steps: 
                self.leg.ee = [trajectory_pos_x, trajectory_pos_y, 0]
                trajectory_pos[0].append(self.leg.ee[0])
                trajectory_pos[1].append(self.leg.ee[1])
                trajectory_angles.append(self.leg.angles)
                trajectory_pos_x += swing_radius/(drag_steps/2)
            else:
                trajectory_pos_y = dist_to_ground + swing_radius * math.sin(theta)
                trajectory_pos_x = swing_radius * math.cos(theta)
                self.leg.ee = [trajectory_pos_x, trajectory_pos_y, 0]
                trajectory_pos[0].append(self.leg.ee[0])
                trajectory_pos[1].append(self.leg.ee[1])
                trajectory_angles.append(self.leg.angles)
                theta += angle_per_step
            
        return trajectory_pos, trajectory_angles
    
    def set_half_circle(self, dist_to_ground, drag_time, swing_time, swing_radius):
        self.trajectory_pos, self.trajectory_angles = self.generate_half_circle(dist_to_ground, drag_time, swing_time, swing_radius)

    def get_next_angles_degrees(self):
        self.check_trajectory_generated()
        angles = np.rad2deg(self.trajectory_angles[self.counter])
        self.counter += 1  
        return angles
    
    def get_next_angles_revolutions(self):
        self.check_trajectory_generated()
        angles = (self.trajectory_angles[self.counter]) / (2 * math.pi)
        if self.counter == (len(self.trajectory_angles) - 1):
            self.counter = 0
        else:
            self.counter += 1
        return angles
    
    def plot(self):
        self.check_trajectory_generated()
        plt.scatter(self.trajectory_pos[0], self.trajectory_pos[1])

        zeroes = []
        joint1_x = []
        joint1_y = []
        joint2_x = []
        joint2_y = []

        for angle in self.trajectory_angles:
            joint1_x.append(self.leg_center_distance * math.cos(angle[0]))
            joint1_y.append(self.leg_center_distance * math.sin(angle[0]))
            joint2_x.append(self.leg_center_distance * math.cos(angle[1] + angle[0]))
            joint2_y.append(self.leg_center_distance * math.sin(angle[1] + angle[0]))
            zeroes.append(0)

        plt.quiver(zeroes, zeroes, joint1_x, joint1_y, color='b', angles='xy', scale_units='xy', scale=1)
        plt.quiver(joint1_x, joint1_y, joint2_x, joint2_y, color='b', angles='xy', scale_units='xy', scale=1)

        # TODO: prob should change limits to generalize to any trajectory 

        plt.xlim(-0.15, 0.2) 
        plt.ylim(-0.3, 0.05) 
        plt.show()
    
    def check_trajectory_generated(self):
        if self.trajectory_pos == None or self.trajectory_angles == None:
            raise Exception("Trajectory type not set")

# example use

# in mm
# leg_center_dist_mm = 175.87
# leg_center_dist_m = leg_center_dist_mm / 1000

# swing_radius_m = 0.05

# drag_time = 0.5
# swing_time = 0.5
# refresh_rate = 0.05
# dist_to_ground = -0.25

# trajectory = Trajectory(refresh_rate, leg_center_dist_m)
# trajectory.set_half_circle(dist_to_ground, drag_time, swing_time, swing_radius=swing_radius_m)
# print(trajectory.get_next_angles_revolutions())
# trajectory.plot()
