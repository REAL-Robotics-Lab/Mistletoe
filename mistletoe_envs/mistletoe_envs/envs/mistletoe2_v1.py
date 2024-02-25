
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
        ctrl_cost_weight=1,
        pitch_cost_weight = 0.5,
        height_cost_weight = 2,
        healthy_reward=0,
        terminate_when_unhealthy=True,
        reset_noise_scale=0.1,
        **kwargs,
    ):
        utils.EzPickle.__init__(
            self,
            xml_file,
            ctrl_cost_weight,
            pitch_cost_weight,
            height_cost_weight,
            healthy_reward,
            terminate_when_unhealthy,
            reset_noise_scale,
            **kwargs,
        )
        self._healthy_reward = healthy_reward
        
        self._ctrl_cost_weight = ctrl_cost_weight
        self._pitch_cost_weight = pitch_cost_weight
        self._height_cost_weight = height_cost_weight

        self._terminate_when_unhealthy = terminate_when_unhealthy

        self._reset_noise_scale = reset_noise_scale

        self._lin_velocity = np.zeros(3)
        self._ang_velocity = np.zeros(3)
        self._ctrl_action = np.zeros(8)

        obs_shape = 46

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

    def is_healthy(self):
        state = self.state_vector()
          
        rot = Rotation.from_quat(state[3:7])
        rot_euler_z = rot.as_euler('xyz', degrees=True)[2]
        is_healthy = np.isfinite(state).all() and abs(rot_euler_z) <= 150 # finite states and not flipped over

        return is_healthy

    def control_cost(self, action):
        control_cost = self._ctrl_cost_weight * np.square(np.linalg.norm(action))
        return control_cost

    # def pitch_cost(self, state):
    #     rot = Rotation.from_quat(state[3:7])
    #     rot_euler_y = rot.as_euler('xyz', degrees=True)[1]

    #     pitch_cost = self._pitch_cost_weight * np.square(rot_euler_y)

    #     return pitch_cost


    def ang_vel_cost(self, ang_velocity):
        pitch_cost = np.square(np.linalg.norm(self._pitch_cost_weight * ang_velocity[:2]))

        return pitch_cost

    # healthy z range is -0.1, 0.1, where 0 is the best
    # def height_cost(self, state):
    #     height = state[2]
    #     height_error = abs(height - 0)
    #     height_cost = self._height_cost_weight * np.square(height_error)

    #     return height_cost

    def z_vel_cost(self, z_velocity):
        return self._height_cost_weight * z_velocity

    @property
    def terminated(self):
        terminated = not self.is_healthy() if self._terminate_when_unhealthy else False
        return terminated

    def step(self, action):
        self._ctrl_action = action

        # retrieve state from before
        xyz_position_before = self.get_body_com("base_link")[:3].copy()
        state_before = self.state_vector()
        self.do_simulation(action * 1, self.frame_skip)
        state_after = self.state_vector()

        xyz_position_after = self.get_body_com("base_link")[:3].copy()
        self._lin_velocity = (xyz_position_after - xyz_position_before) / self.dt
        x_velocity, y_velocity, z_velocity = self._lin_velocity

        rot_before = Rotation.from_quat(state_before[3:7]).as_euler('xyz', degrees=True)
        rot_after = Rotation.from_quat(state_after[3:7]).as_euler('xyz', degrees=True)
        self._ang_velocity = (rot_after - rot_before) / self.dt

        # calculate rewards
        forward_reward = np.exp((-1 * np.square(1 - x_velocity))/0.1)

        #reward for being healthy, and to incentivize not termianting early
        healthy_reward = self._healthy_reward * self.is_healthy()

        rewards = (forward_reward) + healthy_reward

          
        ctrl_cost = self.control_cost(action)
        # pitch_cost = self.pitch_cost(state_after)
        # height_cost = self.height_cost(state_after)

        z_vel_cost = self.z_vel_cost(z_velocity)
        ang_vel_cost = self.ang_vel_cost(self._ang_velocity)

        # costs = ctrl_cost + pitch_cost + height_cost
        costs = ctrl_cost + z_vel_cost + ang_vel_cost

        reward = rewards - costs

        # print(f'heath: {healthy_reward} forward: {np.exp(forward_reward)} ctrl: {ctrl_cost} y_rot:{rot_euler_y} z_rot: {rot_euler_z}')

        print(f'costs: {costs} rewards: {rewards}')
        # print(forward_reward)
        print(x_velocity)
        # print(ctrl_cost)
        # print(pitch_cost)
        # print(height_cost)

        print(forward_reward)

        terminated = self.terminated

        # we substituted rot_after for projected gravity, don't really know how that works

        observation = np.concatenate((self._lin_velocity, self._ang_velocity, rot_after, self.data.qpos.flat.copy(), self.data.qvel.flat.copy(), action))
        info = {
            "reward_forward": forward_reward,
            "reward_ctrl": -ctrl_cost,
            "reward_survive": healthy_reward,
            "x_position": xyz_position_after[0],
            "y_position": xyz_position_after[1],
            "z_position": xyz_position_after[2],
            "distance_from_origin": np.linalg.norm(xyz_position_after[:2], ord=2),
            "x_velocity": x_velocity,
            "y_velocity": y_velocity,
            "forward_reward": forward_reward,
        }
        
        if self.render_mode == "human":
            self.render()
        
        # truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
        return observation, reward, terminated, False, info

    # currently initializes at 0, is that okay?

    def _get_obs(self):
        
        lin_velocity = self._lin_velocity 
        ang_velocity = self._ang_velocity
        base_rotation = Rotation.from_quat(self.data.qpos[3:7]).as_euler('xyz', degrees=True)
        joint_position = self.data.qpos.flat.copy()
        joint_velocity = self.data.qvel.flat.copy()
        action = self._ctrl_action

        return np.concatenate((lin_velocity, ang_velocity, base_rotation, joint_position, joint_velocity, action))

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