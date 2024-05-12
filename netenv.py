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
        self.total_links = len(self.graph.edges())
        self.link_states = {}
        for edge in self.graph.edges():
            self.link_states[edge] = np.zeros(self.num_slots, dtype=int)
        
        self.action_space = spaces.Discrete(self.num_slots * self.total_links * 3)
        self.observation_space = spaces.Box(low=0, high=self.num_slots, shape=(self.total_links * self.num_slots,), dtype=int)

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
        link_index = (action // 3) // self.num_slots
        slot_index = (action // 3) % self.num_slots
        action_type = action % 3

        link = list(self.graph.edges())[link_index]
        if action_type == 0:
            if self.link_states[link][slot_index] < self.num_slots:
                self.link_states[link][slot_index] += 1
                reward = 1
            else:
                reward = -1
        elif action_type == 1:
            if self.link_states[link][slot_index] > 0:
                self.link_states[link][slot_index] -= 1
                reward = 0.5
            else:
                reward = -0.5

        done = np.all(self.link_states[link] == self.num_slots)
        info = {}
        return self.get_observation(), reward, done, False, info


    def get_observation(self):
        obs = []
        for states in self.link_states.values():
            for state in states:
                obs.append(state)
        return np.array(obs)


