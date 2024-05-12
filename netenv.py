import gymnasium as gym
from gymnasium import spaces
import numpy as np
import networkx as nx
import random

class NetworkEnvironment(gym.Env):
    def __init__(self):
        super().__init__()
        self.graph = nx.read_gml('nsfnet.gml')
        self.num_slots = 10 

        self.link_states = {}
        for edge in self.graph.edges():
            self.link_states[edge] = np.zeros(self.num_slots, dtype=int)
        
        total_actions = len(self.graph.edges()) * self.num_slots * 3
        self.action_space = spaces.Discrete(total_actions)
        self.observation_space = spaces.Box(low=0, high=self.num_slots,
                                            shape=(total_actions,), dtype=int)

        self.traffic_requests = self.generate_traffic_requests()

    def generate_traffic_requests(self):
        requests = []
        nodes = list(self.graph.nodes()) 
        for i in range(100):
            src, dst = random.sample(nodes, 2)  
            ht = np.random.randint(10, 20) 
            requests.append((src, dst, ht))
        return requests

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        for edge in self.link_states:
            self.link_states[edge] = np.zeros(self.num_slots, dtype=int)
        return self.get_observation(), {}

    def step(self, action):
        pass


    def get_observation(self):
        obs = []
        for states in self.link_states.values():
            for state in states:
                obs.append(state)
        return np.array(obs)


