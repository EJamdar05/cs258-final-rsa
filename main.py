# RL algorithm
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.dqn import DQNConfig
import ray
# to use a custom env
from ray.tune.registry import register_env

# my custom env
from netenv_test import NetworkEnvironment
import numpy as np

# Just to suppress
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

ray.init()

# registering my custom env with a name "netenv-v0"
def env_creator(env_config):
    return NetworkEnvironment()

register_env('netenv-v0', env_creator)


# Set up RL (PPO)
config_ppo = (PPOConfig()
          .training(gamma=0.999, lr=0.001)
          .environment(env='netenv-v0')
          .resources(num_gpus=0)
          .env_runners(num_env_runners=1, num_envs_per_env_runner=1)
         )

algo_ppo = config_ppo.build()


# Set up RL (DQN)
replay_config = {
        "type": "MultiAgentPrioritizedReplayBuffer",
        "capacity": 60000,
        "prioritized_replay_alpha": 0.5,
        "prioritized_replay_beta": 0.5,
        "prioritized_replay_eps": 3e-6,
    }

config_dqn = (DQNConfig()
          .training(replay_buffer_config=replay_config)
          .environment(env='netenv-v0')
          .resources(num_gpus=0)
          .env_runners(num_env_runners=1, num_envs_per_env_runner=1)
         )

algo_dqn = config_dqn.build()


# Set up agent that doesn't learn
blconfig = (PPOConfig()
          .training(gamma=0.999, lr=0.0)
          .environment(env='netenv-v0')
          .resources(num_gpus=0)
          .env_runners(num_env_runners=0, num_envs_per_env_runner=1)
        )

baseline = blconfig.build()

for _ in range(10):
    algo_ppo.train()
    algo_dqn.train()
    baseline.train()
