import numpy as np

from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box
import pygame
import math

from os import path

assets_dir = path.join(path.dirname(__file__), 'assets', 'mistletoe2_v0')

DEFAULT_CAMERA_CONFIG = {
    "trackbodyid": 0,
    "distance": 2.04,
}

class FirstCartPole(MujocoEnv, utils.EzPickle):
    """
    Observation Space

    +-----+----------------------------------+------+-----+---------------------------------+
    | Num | Observation                      | Min  | Max | Unit                            |
    +-----+----------------------------------+------+-----+---------------------------------+
    | 0   | rotational position of motor 11  | -Inf | Inf | angle (rad)                     |
    | 1   | rotational position of motor 12  | -Inf | Inf | angle (rad)                     |
    | 2   | rotational position of motor 21  | -Inf | Inf | angle (rad)                     |
    | 3   | rotational position of motor 22  | -Inf | Inf | angle (rad)                     |
    | 4   | rotational position of motor 31  | -Inf | Inf | angle (rad)                     |
    | 5   | rotational position of motor 32  | -Inf | Inf | angle (rad)                     |
    | 6   | rotational position of motor 41  | -Inf | Inf | angle (rad)                     |
    | 7   | rotational position of motor 42  | -Inf | Inf | angle (rad)                     |
    | 8   | rotational velocity of motor 11  | -Inf | Inf | angular velocity (rad/s)        |
    | 9   | rotational velocity  of motor 12 | -Inf | Inf | angular velocity (rad/s)        |
    | 10  | rotational velocity of motor 21  | -Inf | Inf | angular velocity (rad/s)        |
    | 11  | rotational velocity of motor 22  | -Inf | Inf | angular velocity (rad/s)        |
    | 12  | rotational velocity of motor 31  | -Inf | Inf | angular velocity (rad/s)        |
    | 13  | rotational velocity of motor 32  | -Inf | Inf | angular velocity (rad/s)        |
    | 14  | rotational velocity of motor 41  | -Inf | Inf | angular velocity (rad/s)        |
    | 15  | rotational velocity of motor 42  | -Inf | Inf | angular velocity (rad/s)        |
    | 16  | base x-axis linear acceleration  | -Inf | Inf | linear acceleration (m/s^2)     |
    | 17  | base y-axis linear acceleration  | -Inf | Inf | linear acceleration (m/s^2)     |
    | 18  | base z-axis linear acceleration  | -Inf | Inf | linear acceleration (m/s^2)     |
    | 19  | base roll acceleration           | -Inf | Inf | rotational acceleration (m/s^2) |
    | 20  | base pitch acceleration          | -Inf | Inf | rotational acceleration (m/s^2) |
    | 21  | base yaw acceleration            | -Inf | Inf | rotational acceleration (m/s^2) |
    +-----+----------------------------------+------+-----+---------------------------------+
    """

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 250,
    }


    def __init__(self, **kwargs):
        self.window = None

        self.prev_lin_velocity = np.zeros(3)
        self.prev_ang_velocity = np.zeros(3)

        self.base_lin_velocity = np.zeros(3)
        self.base_ang_velocity = np.zeros(3)

        self.target_velocity_x = 0

        utils.EzPickle.__init__(self, **kwargs)
        
        observation_space = Box(low=-np.inf, high=np.inf, shape=(22,), dtype=np.float64)

        MujocoEnv.__init__(
            self,
            assets_dir + "/quadurdf.xml",
            2,
            observation_space=observation_space,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            **kwargs,
        )

    def step(self, a):
        self.do_simulation(a, self.frame_skip)

        observation = self._get_obs()
        terminated = bool(
            not np.isfinite(observation).all() or (np.abs(observation[1]) > 2)
        )

        reward = int(not terminated)

        info = {"reward_survive": reward}

        if self.render_mode == "human":
            self.render()
        # truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
        return observation, reward, terminated, False, info
    
    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(
            size=self.model.nq, low=-0.01, high=0.01
        )
        qvel = self.init_qvel + self.np_random.uniform(
            size=self.model.nv, low=-0.01, high=0.01
        )
        self.set_state(qpos, qvel)

        self.target_lin_velocity_x = np.random.uniform(-1, 1) # TODO: find feasible velocity params
        self.target_ang_velocity_xy = np.zeros(2)
        
        return self._get_obs()

    def _get_obs(self):
        position = self.data.qpos.flatten()
        velocity = self.data.qvel.flatten()

        lin_acceleration = self.data.sensordata.flatten()[0]
        ang_acceleration = self.data.sensordata.flatten()[1]
        
        self.base_lin_velocity = np.add(self.prev_lin_velocity, (lin_acceleration * self.dt))
        self.base_ang_velocity = np.add(self.prev_ang_velocity, (ang_acceleration * self.dt))
        
        self.prev_lin_velocity = self.base_lin_velocity
        self.prev_ang_velocity = self.base_ang_velocity

        real_velocity = self.data.sensordata.flatten()[2]

        print(f'Real velocities: {real_velocity} Calculated velocities: {self.base_lin_velocity}')

        return np.concatenate([position, velocity, self.base_lin_velocity, self.base_ang_velocity, self.target_velocity_x])
    
    def _get_rew(self):

        base_lin_velocity_x = self.base_lin_velocity[0]
        base_lin_velocity_z = self.base_lin_velocity[2]

        base_ang_velocity_xy = self.base_ang_velocity[0:2]

        # base_ang_velocity_z = base_ang_velocity[0]
        # ang_vel_reward = np.exp(-1 * abs(target_ang_velocity_z - base_ang_velocity_z))

        # reward from https://arxiv.org/abs/2203.05194 and https://github.com/Gepetto/soloRL/blob/master/Environment.hpp
        
        # going forward is good 
        lin_vel_reward = np.exp((self.target_lin_velocity_x - base_lin_velocity_x)) * self.lin_vel_reward_weight

        # not being parallel to the ground is bad
        ang_vel_penalty = -1 * np.power(np.linalg.norm(self.target_ang_velocity_xy - base_ang_velocity_xy), 2) * self.ang_vel_penalty_weight
        
        # using too much power is bad
        torque_penalty = -1 * np.power(np.linalg.norm(self.data.qfrc_actuator), 2) * self.torque_penalty_weight

        #going up and down is bad
        lin_vel_penalty = -1 * np.power(base_lin_velocity_z, 2) * self.lin_vel_penalty_weight

        total_reward = lin_vel_reward + ang_vel_penalty + torque_penalty + lin_vel_penalty

        return total_reward



