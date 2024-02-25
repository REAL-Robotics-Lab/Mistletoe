from gymnasium.envs.registration import register

register(
     id="mistletoe_envs/Mistletoe2-v0",
     entry_point="mistletoe_envs.envs.mistletoe2_v0:Mistletoe2",
     max_episode_steps=1000,
)

register(
     id="mistletoe_envs/Mistletoe2-v1",
     entry_point="mistletoe_envs.envs.mistletoe2_v1:Mistletoe2",
     max_episode_steps=1000,
)
