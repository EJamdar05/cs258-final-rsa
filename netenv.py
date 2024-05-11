import gym
from gym import spaces
import numpy as np
import networkx as nx

class NetworkEnvironment(gym.Env):
    def __init__(self, env_config=None):
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
        
        

    def reset(self, seed = None, options = None):
        super().reset(seed = seed)
        self.utilization = np.zeros((self.num_links, self.num_slots), dtype=int)
        self.current_request = self.generate_request()
        info = {}
        return self.get_observation(), info

    def step(self, action):
        node, slot, action_type = action
        reward = 0
        self.round += 1
        terminated = (self.round == 20)

        #allocate a color and the slot is free
        if action_type == 1 and self.utilization[node, slot] == 0:
            self.utilization[node, slot] = 1
            reward = 1
        #remove color assuming that the link is in use
        elif action_type == 0 and self.utilization[node, slot] == 1:
            self.utilization[node, slot] = 0
            reward = 1
        #negative reward (conditons failed above)
        else:
            reward = -1
        
        #end the episode if all links used or all rounds finished
        done = False
        if np.all(self.utilization) or terminated:
            done = True

        self.current_request = self.generate_request()
        info = {}
        return self.get_observation(), reward, done, info

    def generate_request(self):
        src = np.random.randint(0, self.num_nodes)
        dst = np.random.randint([i for i in range(self.num_nodes) if i != src])
        ht = np.random.randint(10, 20)
        return (src, dst, ht)

    def get_observation(self):
        return {
            "links": self.utilization,
            "req": np.array(self.current_request, dtype=float)
        }
