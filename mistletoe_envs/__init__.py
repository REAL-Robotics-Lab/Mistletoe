from gymnasium.envs.registration import register

register(
     id="mistletoe_envs/Mistletoe2-v0",
     entry_point="mistletoe_envs.envs.mistletoe2_v0:FirstCartPole",
     max_episode_steps=1000,
)