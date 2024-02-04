from mistletoe_envs.envs.mistletoe2_v0 import Mistletoe2
import gymnasium
import numpy as np
from stable_baselines3 import A2C, PPO, TD3
from stable_baselines3.common.env_util import make_vec_env
import os
from stable_baselines3.common.callbacks import EvalCallback

from stable_baselines3.common.env_util import make_vec_env

import time

model = TD3.load("./eval_logs/best_model.zip", print_system_info=True)

vec_env = make_vec_env('mistletoe_envs/Mistletoe2-v0', n_envs=1, seed=3)
obs = vec_env.reset()
for i in range(10000):
    action, _state = model.predict(obs, deterministic=True)
    obs, reward, done, info = vec_env.step(action)
    print(reward)
    # print('test' + str(obs))
    vec_env.render("human")