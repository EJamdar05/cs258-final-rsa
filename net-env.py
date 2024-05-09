import gymnasium as gym
from gym import spaces
import numpy as np 
from ray.rllib.algorithms.ppo import PPOConfig
import networkx as nx

class NetworkEnvironment(gym.Env):
    def __init__(self) -> None:
        self.graph = nx.read_gml("nsfnet.gml")
        self.num_nodes = len(self.graph)
        self.edges = list(self.graph.edges)
        self.num_links = len(self.edges)
        self.num_slots = 5

        self.observation_space = spaces.Dict(
            {
                "links" : spaces.Box(0, 1, shape=(self.num_links,), dtype = int),
                "req" : spaces.Box([0,0,10], [self.num_nodes - 1, self.num_nodes - 1, 20], 
                                   shape=(1, ), dtype=int)
            }
        )

        self.action_space = spaces.MultiDiscrete([self.num_nodes, self.num_slots, 2])
        self.round = 0

        self.utilization = np.zeros((self.num_nodes, self.num_slots), dtype=int)
        self.current_request = None
        

        def reset(self):
            self.utilization = np.zeros((self.num_nodes, self.num_slots), dtype=int)
            self.current_request = generate_request()
        
        def generate_request(self):
            return np.array([np.random.randint(1, 3+1), ])

