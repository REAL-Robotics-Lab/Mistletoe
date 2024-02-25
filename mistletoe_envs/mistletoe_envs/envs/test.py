from mistletoe_envs.envs.mistletoe2_v0 import Mistletoe2
import gymnasium
import numpy as np
from stable_baselines3 import A2C, TD3, PPO
from stable_baselines3.common.env_util import make_vec_env
import os
from stable_baselines3.common.callbacks import EvalCallback

env_id = 'mistletoe_envs/Mistletoe2-v1'
n_training_envs = 1 
n_eval_envs = 5

# Create log dir where evaluation results will be saved
eval_log_dir = "./eval_logs/"
os.makedirs(eval_log_dir, exist_ok=True)

train_env = make_vec_env(env_id, n_envs=n_training_envs, seed=0)
eval_env = make_vec_env(env_id, n_envs=n_eval_envs, seed=0)

eval_callback = EvalCallback(eval_env, best_model_save_path=eval_log_dir,
                              log_path=eval_log_dir, eval_freq=max(500 // n_training_envs, 1),
                              n_eval_episodes=5, deterministic=True,
                              render=False)

model = TD3("MlpPolicy", train_env)
model.learn(total_timesteps=5000, callback=eval_callback)

# env = gymnasium.make('firstrl/FirstCartPole-v0', render_mode='rgb_array')
# model = A2C("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=100_000)

vec_env = model.get_env()
obs = vec_env.reset()
for i in range(1000):
    action, _state = model.predict(obs, deterministic=True)
    obs, reward, done, info = vec_env.step(action)
    print(obs)
    print(reward)
    vec_env.render("human")