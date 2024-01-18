from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import math
import tinyik
import csv

from os import path


def radians_to_revs(angle_radians):
    return angle_radians / (2 * math.pi)


class Trajectory(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.length = 0

    @abstractmethod
    def get_state(self, counter: int) -> tuple[tuple[float, float], tuple[float, float]]:
        pass


class PredeterminedTrajectory(Trajectory):
    length: int

    second_ik: bool

    leg_center_distance_1: float
    leg_center_distance_2: float

    angles = []
    # velocities = []

    def __init__(self, leg_center_distance_1=None, leg_center_distance_2=None, filepath=None, second_ik=False) -> None:
        # variables that are used by subclasses' trajectory generation should be listed up here
        
        self.second_ik = second_ik

        self.finished = False
        if filepath is not None and path.exists(filepath):
            print("  Reading trajectory from file...")
            self.load_trajectory(filepath)
        else:
            print("  Generating trajectory...")
            self.leg_center_distance_1 = leg_center_distance_1
            self.leg_center_distance_2 = leg_center_distance_2
            self.angles = self.generate_trajectory()
        self.length = len(self.angles)
        

        if filepath and not path.exists(filepath):
            self.save_trajectory(filepath=filepath)

    def get_finished(self) -> bool:
        return self.finished

    def get_state(self, pos: int) -> tuple[tuple[float, float], tuple[float, float]]:
        if pos >= self.length - 1:
            pos = self.length - 1
                
        # convert to revs
        angle = (
            radians_to_revs((self.angles[pos][0])),
            radians_to_revs((self.angles[pos][1])),
        )

        return angle

    @abstractmethod
    def generate_trajectory(self) -> tuple[list[tuple], list[tuple]]:
        pass

    def plot(self):
        zeroes = []
        joint1_x = []
        joint1_y = []
        joint2_x = []
        joint2_y = []

        for angle in self.angles:
            joint1_y.append(self.leg_center_distance_1 * math.sin(angle[0] - math.pi / 2))
            joint1_x.append(self.leg_center_distance_1 * math.cos(angle[0] - math.pi / 2))
            joint2_y.append(self.leg_center_distance_2 * math.sin(angle[1] + angle[0] - math.pi / 2))
            joint2_x.append(self.leg_center_distance_2 * math.cos(angle[1] + angle[0] - math.pi / 2))
            zeroes.append(0)

        plt.quiver(
            zeroes,
            zeroes,
            joint1_x,
            joint1_y,
            color="b",
            angles="xy",
            scale_units="xy",
            scale=1,
        )
        plt.quiver(
            joint1_x,
            joint1_y,
            joint2_x,
            joint2_y,
            color="b",
            angles="xy",
            scale_units="xy",
            scale=1,
        )

        # TODO: prob should change limits to generalize to any trajectory

        plt.xlim(-0.3, 0.3)
        plt.ylim(-0.3, 0.3)
        plt.show()

    def save_trajectory(self, filepath):
        with open(filepath, newline='', mode='w') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quotechar='|')
            for [hip, knee] in self.angles:
                writer.writerow([hip, knee])

    def load_trajectory(self, filepath):
        self.angles = []
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for [hip, knee] in reader:
                self.angles.append((float(hip), float(knee)))
    
    # find the second solution of ik given 2 joints
    def find_second_ik(self,theta_1, theta_2, x, y):
        theta_1 = - theta_1 - 2 * math.copysign(math.acos(y / math.sqrt(y*y+x*x)), x)
        theta_2 = theta_2 * -1 
        return theta_1, theta_2


class HalfCircleTrajectory(PredeterminedTrajectory):
    num_setpoints: int

    num_setpoints_swing: int
    num_setpoints_drag: int

    dist_to_ground: float
    swing_radius: float

    leg_ik: tinyik.Actuator

    x_offset: float

    def __init__(
        self,
        dist_to_ground=None,
        leg_center_distance_1=None,
        leg_center_distance_2=None,
        filepath=None,
        num_setpoints=None,
        swing_radius=None,
        second_ik=False,
        x_offset = 0
    ) -> None:
        if filepath is not None:
            self.load_trajectory(filepath)

            super().__init__(filepath=filepath)
        else:
            self.num_setpoints = num_setpoints

            # self.num_setpoints_swing = int((math.pi / (2 + math.pi)) * num_setpoints)
            # self.num_setpoints_drag = int((2 / (2 + math.pi)) * num_setpoints)

            # setpoints and therefore time for each phase should be the same
            self.num_setpoints_drag = int(num_setpoints/2)
            self.num_setpoints_swing = int(num_setpoints/2)

            self.leg_ik = tinyik.Actuator(
                ["z", [0.0, leg_center_distance_1, 0.0], "z", [0.0, leg_center_distance_2, 0.0]]
            )

            self.swing_radius = swing_radius

            self.dist_to_ground = dist_to_ground

            self.x_offset = x_offset

            super().__init__(leg_center_distance_1=leg_center_distance_1, leg_center_distance_2=leg_center_distance_2, second_ik=second_ik)
        

    def generate_trajectory(self) -> tuple[list[tuple], list[tuple]]:  
        #offset
        trajectory_pos_x = 0 + self.x_offset

        trajectory_pos_y = self.dist_to_ground  # init @ dist to ground

        self.leg_ik.ee = [trajectory_pos_x, trajectory_pos_y, 0]

        angle_per_step = math.pi / self.num_setpoints_swing
        theta = 0

        angles = []

        for step_counter in range(self.num_setpoints):
            if (
                step_counter < self.num_setpoints_drag / 2
                or step_counter > self.num_setpoints_drag / 2 + self.num_setpoints_swing
            ):

                # ik solver breaks for 0,0 for some reason
                if trajectory_pos_x == 0:
                    trajectory_pos_x = 0.0001
                if trajectory_pos_y == 0:
                    trajectory_pos_y = 0.0001

                self.leg_ik.ee = [trajectory_pos_x, trajectory_pos_y, 0]

                if self.second_ik == True:
                    theta_1, theta_2 = self.find_second_ik(self.leg_ik.angles[0], self.leg_ik.angles[1], trajectory_pos_x, trajectory_pos_y)
                else:
                    theta_1, theta_2 = self.leg_ik.angles[0], self.leg_ik.angles[1]
                
                angle = theta_1, theta_2

                angles.append(angle)
                # velocities.append((self.uniform_velocity, self.uniform_velocity))

                trajectory_pos_x += self.swing_radius / (self.num_setpoints_drag / 2)
                trajectory_pos_y = self.dist_to_ground
            else:
                theta += angle_per_step
                trajectory_pos_y = self.dist_to_ground - self.swing_radius * math.sin(
                    theta
                )
                # print('theta: ' + str(theta))
                # print('sin * rad: ' + str(self.swing_radius * math.sin(theta)))
                # print('should be 0: ' + str(math.sin(theta)))
                trajectory_pos_x = self.swing_radius * math.cos(theta) + self.x_offset

                # ik solver breaks for 0,0 for some reason
                if trajectory_pos_x == 0:
                    trajectory_pos_x = 0.0001
                if trajectory_pos_y == 0:
                    trajectory_pos_y = 0.0001

                self.leg_ik.ee = [trajectory_pos_x, trajectory_pos_y, 0]

                if self.second_ik == True:
                    theta_1, theta_2 = self.find_second_ik(self.leg_ik.angles[0], self.leg_ik.angles[1], trajectory_pos_x, trajectory_pos_y)
                else:
                    theta_1, theta_2 = self.leg_ik.angles[0], self.leg_ik.angles[1]
                
                angle = theta_1, theta_2

                angles.append(angle)
                # velocities.append((self.uniform_velocity, self.uniform_velocity))
            # print(f'{trajectory_pos_x}, {trajectory_pos_y}')
            # print(theta)
            # print(self.swing_radius * math.sin(theta))
        # print(angles)
        return angles


class StandingTrajectory(PredeterminedTrajectory):
    dist_to_ground: float
    leg_ik: tinyik.Actuator
    x_offset: float

    def __init__(self, leg_center_distance_1, leg_center_distance_2, dist_to_ground, filepath=None, second_ik=False, x_offset = 0) -> None:
        self.dist_to_ground = dist_to_ground
        self.leg_ik = tinyik.Actuator(
            ["z", [0.0, leg_center_distance_1, 0.0], "z", [0.0, leg_center_distance_2, 0.0]]
        )
        self.x_offset = x_offset
        super().__init__(leg_center_distance_1, leg_center_distance_2, filepath=filepath, second_ik=second_ik)

    def generate_trajectory(self) -> tuple[list[tuple], list[tuple]]:
        x = self.x_offset
        y = self.dist_to_ground

        if x == 0:
            x = 0.0001

        # ik solver breaks for x=0 for some reason
        self.leg_ik.ee = [x ,self.dist_to_ground, 0]

        if self.second_ik == True:
            print('second ik is true')
            theta_1, theta_2 = self.find_second_ik(self.leg_ik.angles[0], self.leg_ik.angles[1], x, y)
        else:
            print('second ik is false')
            theta_1, theta_2 = self.leg_ik.angles[0] , self.leg_ik.angles[1]
        angle = (theta_1, theta_2)
        return [angle]


class GetUpTrajectory(PredeterminedTrajectory):
    num_setpoints: int
    dist_to_ground: float
    uniform_velocity: float
    leg_ik: tinyik.Actuator

    def __init__(self, num_setpoints: int, dist_to_ground: float, uniform_velocity: float):
        self.num_setpoints = num_setpoints
        self.dist_to_ground = dist_to_ground
        self.uniform_velocity = uniform_velocity

    def generate_trajectory(self) -> tuple[list[tuple], list[tuple]]:
        trajectory_pos_x = 0
        # init a little below the rotational point
        trajectory_pos_y = self.dist_to_ground / 10

        self.leg_ik.ee = [trajectory_pos_x, trajectory_pos_y, 0]

        remaining_length = self.dist_to_ground * 9 / 10
        y_increment = remaining_length / self.num_setpoints

        angles = []

        for step in range(self.num_setpoints):
            trajectory_pos_y += y_increment
            angles.append(self.leg_ik.angles[0], self.leg_ik.angles[1])
        
        return angles, [(self.uniform_velocity, self.uniform_velocity) for i in range(self.num_setpoints)]

if __name__ == "__main__":
    leg_center_dist_1_mm = 175.87
    leg_center_dist_1_m = leg_center_dist_1_mm / 1000

    leg_center_dist_2_mm = 175.87
    leg_center_dist_2_m = leg_center_dist_2_mm / 1000

    swing_radius_m = 0.05

    drag_time = 0.5
    swing_time = 0.5
    refresh_rate = 0.05
    dist_to_ground = 0.25

    trajectory = HalfCircleTrajectory(leg_center_distance_1 = leg_center_dist_1_m, leg_center_distance_2=leg_center_dist_2_m, dist_to_ground=dist_to_ground, num_setpoints=10, swing_radius=swing_radius_m, second_ik=True, x_offset=0.05)
    # trajectory = StandingTrajectory(leg_center_distance_1=leg_center_dist_1_m, leg_center_distance_2=leg_center_dist_2_m, dist_to_ground=dist_to_ground, second_ik=True,  x_offset=0.05)
    print(trajectory.get_state(1))
    trajectory.plot()


