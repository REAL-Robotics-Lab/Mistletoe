# import numpy as np

# from gymnasium import utils
# from gymnasium.envs.mujoco import MujocoEnv
# from gymnasium.spaces import Box
# import pygame
# import math

# from os import path

# assets_dir = path.join(path.dirname(__file__), 'assets', 'mistletoe2_v0')

# DEFAULT_CAMERA_CONFIG = {
#     "trackbodyid": 0,
#     "distance": 2.04,
# }

# class Mistletoe2(MujocoEnv, utils.EzPickle):
#     """
#     Observation Space

#     +-----+----------------------------------+------+-----+---------------------------------+
#     | Num | Observation                      | Min  | Max | Unit                            |
#     +-----+----------------------------------+------+-----+---------------------------------+
#     | 0   | rotational position of motor 11  | -Inf | Inf | angle (rad)                     |
#     | 1   | rotational position of motor 12  | -Inf | Inf | angle (rad)                     |
#     | 2   | rotational position of motor 21  | -Inf | Inf | angle (rad)                     |
#     | 3   | rotational position of motor 22  | -Inf | Inf | angle (rad)                     |
#     | 4   | rotational position of motor 31  | -Inf | Inf | angle (rad)                     |
#     | 5   | rotational position of motor 32  | -Inf | Inf | angle (rad)                     |
#     | 6   | rotational position of motor 41  | -Inf | Inf | angle (rad)                     |
#     | 7   | rotational position of motor 42  | -Inf | Inf | angle (rad)                     |
#     | 8   | rotational velocity of motor 11  | -Inf | Inf | angular velocity (rad/s)        |
#     | 9   | rotational velocity  of motor 12 | -Inf | Inf | angular velocity (rad/s)        |
#     | 10  | rotational velocity of motor 21  | -Inf | Inf | angular velocity (rad/s)        |
#     | 11  | rotational velocity of motor 22  | -Inf | Inf | angular velocity (rad/s)        |
#     | 12  | rotational velocity of motor 31  | -Inf | Inf | angular velocity (rad/s)        |
#     | 13  | rotational velocity of motor 32  | -Inf | Inf | angular velocity (rad/s)        |
#     | 14  | rotational velocity of motor 41  | -Inf | Inf | angular velocity (rad/s)        |
#     | 15  | rotational velocity of motor 42  | -Inf | Inf | angular velocity (rad/s)        |
#     | 16  | base x-axis linear acceleration  | -Inf | Inf | linear acceleration (m/s^2)     |
#     | 17  | base y-axis linear acceleration  | -Inf | Inf | linear acceleration (m/s^2)     |
#     | 18  | base z-axis linear acceleration  | -Inf | Inf | linear acceleration (m/s^2)     |
#     | 19  | base roll acceleration           | -Inf | Inf | rotational acceleration (m/s^2) |
#     | 20  | base pitch acceleration          | -Inf | Inf | rotational acceleration (m/s^2) |
#     | 21  | base yaw acceleration            | -Inf | Inf | rotational acceleration (m/s^2) |
#     +-----+----------------------------------+------+-----+---------------------------------+
#     """

#     metadata = {
#         "render_modes": [
#             "human",
#             "rgb_array",
#             "depth_array",
#         ],
#         "render_fps": 250,
#     }


#     def __init__(self, lin_vel_reward_weight = 1, ang_vel_penalty_weight = 0.05, torque_penalty_weight = 0.2, lin_vel_penalty_weight=2, **kwargs):

#         self.lin_vel_reward_weight = lin_vel_reward_weight
#         self.ang_vel_penalty_weight = ang_vel_penalty_weight
#         self.torque_penalty_weight = torque_penalty_weight
#         self.lin_vel_penalty_weight = lin_vel_penalty_weight

#         self.dsad = 0

#         self.window = None

#         utils.EzPickle.__init__(self, **kwargs)
        
#         observation_space = Box(low=-np.inf, high=np.inf, shape=(23,), dtype=np.float64)

#         MujocoEnv.__init__(
#             self,
#             assets_dir + "/quadurdf.xml",
#             2,
#             observation_space=observation_space,
#             default_camera_config=DEFAULT_CAMERA_CONFIG,
#             **kwargs,
#         )

#     def step(self, a):
#         self.do_simulation(a, self.frame_skip)

#         lin_acceleration = self.data.sensordata[0:3]
#         ang_acceleration = self.data.sensordata.flatten()[3:6]

#         b = self.dsad

#         self.dsad = (self.data.sensordata[6])

#         self.base_lin_velocity = np.add(self.prev_lin_velocity, (lin_acceleration * self.dt))
#         self.base_ang_velocity = np.add(self.prev_ang_velocity, (ang_acceleration * self.dt))
        
#         self.prev_lin_velocity = self.base_lin_velocity
#         self.prev_ang_velocity = self.base_ang_velocity

#         observation = self._get_obs()
#         terminated = bool(
#             not np.isfinite(observation).all() or (np.abs(observation[1]) > 2)
#         )

#         reward = self._get_rew()

#         info = {"reward_survive": reward}

#         if self.render_mode == "human":
#             self.render()
#         # truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
#         return observation, reward, terminated, False, info
    
#     def reset_model(self):
#         qpos = self.init_qpos + self.np_random.uniform(
#             size=self.model.nq, low=-0.01, high=0.01
#         )
#         qvel = self.init_qvel + self.np_random.uniform(
#             size=self.model.nv, low=-0.01, high=0.01
#         )
#         self.set_state(qpos, qvel)

#         self.prev_lin_velocity = np.zeros(3)
#         self.prev_ang_velocity = np.zeros(3)

#         self.base_lin_velocity = np.zeros(3)
#         self.base_ang_velocity = np.zeros(3)

#         self.target_lin_velocity_x = np.random.uniform(-1, 1) # TODO: find feasible velocity params
#         self.target_ang_velocity = np.zeros(3) # we don't want to be turning the base at all
        
#         return self._get_obs()

#     def _get_obs(self):
#         position = self.data.qpos[7:].flatten()
#         # print(len(position))
#         velocity = self.data.qvel[6:].flatten()
#         # print(len(velocity))
#         base_lin_velocity = self.base_lin_velocity.flatten()
#         base_ang_velocity = self.base_ang_velocity.flatten()

#         real_velocity = (self.data.sensordata[6])
#         # print(len(self.base_lin_velocity))

#         # print(f'Real velocities: {real_velocity} Calculated velocities: {self.base_lin_velocity[0]} diff: {real_velocity-self.base_lin_velocity[0]}')

#         # same as https://arxiv.org/abs/2203.05194 aside from the ones that aren't relevant to pos control
#         # print(self.target_lin_velocity_x)
#         return np.concatenate([position, velocity, base_lin_velocity, base_ang_velocity, [self.target_lin_velocity_x]])
    
#     def _get_rew(self):

#         base_lin_velocity_x = self.base_lin_velocity[0]

#         # print('fuckin' + str(base_lin_velocity_x))
#         base_lin_velocity_z = self.base_lin_velocity[2]

#         # base_ang_velocity_z = base_ang_velocity[0]
#         # ang_vel_reward = np.exp(-1 * abs(target_ang_velocity_z - base_ang_velocity_z))

#         # reward from https://arxiv.org/abs/2203.05194 and https://github.com/Gepetto/soloRL/blob/master/Environment.hpp
        
#         # going forward is good 
#         lin_vel_reward = -1 * (self.target_lin_velocity_x - base_lin_velocity_x) * self.lin_vel_reward_weight

#         # turning at all is bad
#         ang_vel_penalty = -1 * np.power(np.linalg.norm(self.target_ang_velocity - self.base_ang_velocity), 2) * self.ang_vel_penalty_weight
        
#         # using too much power is bad
#         torque_penalty = -1 * np.power(np.linalg.norm(self.data.qfrc_actuator), 2) * self.torque_penalty_weight

#         torque_penalty = 0
#         #going up and down is bad
#         lin_vel_penalty = -1 * np.power(base_lin_velocity_z, 2) * self.lin_vel_penalty_weight

#         total_reward = lin_vel_reward #+ torque_penalty + lin_vel_penalty

#         return total_reward

import numpy as np

from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box
import os 

import pandas as pd
from scipy.spatial.transform import Rotation

import math

DEFAULT_CAMERA_CONFIG = {
    "distance": 4.0,
}


class Mistletoe2(MujocoEnv, utils.EzPickle):
    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 100,
    }

    def __init__(
        self,
        xml_file= os.path.join(os.path.dirname(__file__), 'assets', 'mistletoe2_v0', 'quadurdf.xml'),
        ctrl_cost_weight=0.5,
        use_contact_forces=False,
        contact_cost_weight=5e-4,
        healthy_reward=1.0,
        terminate_when_unhealthy=True,
        healthy_z_range=(-0.125, 1),
        contact_force_range=(-1.0, 1.0),
        reset_noise_scale=0.1,
        exclude_current_positions_from_observation=True,
        **kwargs,
    ):
        utils.EzPickle.__init__(
            self,
            xml_file,
            ctrl_cost_weight,
            use_contact_forces,
            contact_cost_weight,
            healthy_reward,
            terminate_when_unhealthy,
            healthy_z_range,
            contact_force_range,
            reset_noise_scale,
            exclude_current_positions_from_observation,
            **kwargs,
        )

        self._ctrl_cost_weight = ctrl_cost_weight
        self._contact_cost_weight = contact_cost_weight

        self._healthy_reward = healthy_reward
        self._terminate_when_unhealthy = terminate_when_unhealthy
        self._healthy_z_range = healthy_z_range

        self._contact_force_range = contact_force_range

        self._reset_noise_scale = reset_noise_scale

        self._use_contact_forces = use_contact_forces

        self._exclude_current_positions_from_observation = (
            exclude_current_positions_from_observation
        )

        obs_shape = 27
        if not exclude_current_positions_from_observation:
            obs_shape += 2
        if use_contact_forces:
            obs_shape += 84

        observation_space = Box(
            low=-np.inf, high=np.inf, shape=(obs_shape,), dtype=np.float64
        )

        MujocoEnv.__init__(
            self,
            xml_file,
            5,
            observation_space=observation_space,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            **kwargs,
        )

    @property
    def healthy_reward(self):
        return (
            float(self.is_healthy or self._terminate_when_unhealthy)
            * self._healthy_reward
        )

    def control_cost(self, action):
        control_cost = self._ctrl_cost_weight * np.sum(np.square(action))
        return control_cost

    @property
    def contact_forces(self):
        raw_contact_forces = self.data.cfrc_ext
        min_value, max_value = self._contact_force_range
        contact_forces = np.clip(raw_contact_forces, min_value, max_value)
        return contact_forces

    @property
    def contact_cost(self):
        contact_cost = self._contact_cost_weight * np.sum(
            np.square(self.contact_forces)
        )
        return contact_cost
    
    @property
    def is_healthy(self):
        state = self.state_vector()
          
        rot = Rotation.from_quat(state[3:7])
        rot_euler_z = rot.as_euler('xyz', degrees=True)[2]
        rot_euler_y = rot.as_euler('xyz', degrees=True)[1]
        # print(abs(rot_euler_z)>20)
        # print(rot_euler_z)
        min_z, max_z = self._healthy_z_range
        is_healthy = np.isfinite(state).all() and abs(rot_euler_z) <= 150 # and abs(rot_euler_z)<45 and abs(rot_euler_y) < 45 and state[2]<0.2
        # print(rot_euler_z)
        # print(self.get_body_com("base_link")[2])
        # print(len(state))
        # if not min_z <= state[2] <= max_z:
        #     print('hi')


        return is_healthy

    @property
    def terminated(self):
        terminated = not self.is_healthy if self._terminate_when_unhealthy else False
        return terminated

    def step(self, action):
        xy_position_before = self.get_body_com("base_link")[:2].copy()
        # print(action)
        self.do_simulation(action * 1, self.frame_skip)
        xy_position_after = self.get_body_com("base_link")[:2].copy()

        xy_velocity = (xy_position_after - xy_position_before) / self.dt
        x_velocity, y_velocity = xy_velocity

        forward_reward = np.exp(np.square(1-x_velocity) * 0.25)
        healthy_reward = self.healthy_reward

        rewards = (forward_reward) + healthy_reward

        # print(forward_reward)
        # print(healthy_reward)

        # print(action)
        state = self.state_vector()
          
        rot = Rotation.from_quat(state[3:7])
        rot_euler_z = rot.as_euler('xyz', degrees=True)[2]
        rot_euler_y = rot.as_euler('xyz', degrees=True)[1]
        ctrl_cost = abs(self.control_cost(action))
        costs = ctrl_cost+ abs(rot_euler_y) + abs(rot_euler_z)

        # print(f'heath: {healthy_reward} forward: {np.exp(forward_reward)} ctrl: {ctrl_cost} y_rot:{rot_euler_y} z_rot: {rot_euler_z}')


        # print(f'costs: {costs} rewards: {rewards}')

        terminated = self.terminated
        observation = self._get_obs()
        info = {
            "reward_forward": forward_reward,
            "reward_ctrl": -ctrl_cost,
            "reward_survive": healthy_reward,
            "x_position": xy_position_after[0],
            "y_position": xy_position_after[1],
            "distance_from_origin": np.linalg.norm(xy_position_after, ord=2),
            "x_velocity": x_velocity,
            "y_velocity": y_velocity,
            "forward_reward": forward_reward,
        }
        if self._use_contact_forces:
            contact_cost = self.contact_cost
            costs += contact_cost
            info["reward_ctrl"] = -contact_cost

        reward = rewards - costs
        # print(reward)


        if self.render_mode == "human":
            self.render()
        # truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
        return observation, reward, terminated, False, info

    def _get_obs(self):
        position = self.data.qpos.flat.copy()
        velocity = self.data.qvel.flat.copy()

        if self._exclude_current_positions_from_observation:
            position = position[2:]

        if self._use_contact_forces:
            contact_force = self.contact_forces.flat.copy()
            return np.concatenate((position, velocity, contact_force))
        else:
            return np.concatenate((position, velocity))

    def reset_model(self):
        noise_low = -self._reset_noise_scale
        noise_high = self._reset_noise_scale

        qpos = self.init_qpos + self.np_random.uniform(
            low=noise_low, high=noise_high, size=self.model.nq
        )
        qvel = (
            self.init_qvel
            + self._reset_noise_scale * self.np_random.standard_normal(self.model.nv)
        )
        self.set_state(qpos, qvel)

        observation = self._get_obs()

        return observation

