import gymnasium as gym
from gymnasium import spaces
import numpy as np
import networkx as nx
import random

class NetworkEnvironment(gym.Env):
    def __init__(self):
        super().__init__()
        #Read the network file
        self.graph = nx.read_gml('nsfnet.gml')
        #Max utilization per slot
        self.num_slots = 10
        #Total edges/links
        self.total_links = len(self.graph.edges())

        #State of links
        self.link_states = {}
        for edge in self.graph.edges():
            #initialize the state of all edge utilization to 0
            self.link_states[edge] = np.zeros(self.num_slots, dtype=int)

        self.isRandom = True
        #generate list of traffic requests (100)
        self.traffic_requests = self.generate_traffic_requests()
        #generate the shortest paths from traffic reqs
        self.paths = self.generate_paths()

        self.action_space = spaces.Discrete(len(self.paths))
        print(len(self.paths))
        self.observation_space = spaces.Box(low=0, high=20, shape=(self.total_links * self.num_slots,), dtype=int)
        self.current_request_index = 0

    def generate_paths(self):
        paths = []
        for s, d, _, in self.traffic_requests:
            paths = paths + list(nx.shortest_simple_paths(self.graph, source=s, target=d))
        return paths

    def generate_traffic_requests(self):
        requests = []
        nodes = list(self.graph.nodes()) 
        for i in range(100):
            if not self.isRandom:
                src = "San Diego Supercomputer Center"
                dst = "Jon Von Neumann Center, Princeton, NJ"
            else:
                src, dst = random.sample(nodes, 2)  
            ht = np.random.randint(10, 20) 
            requests.append((src, dst, ht))
        return requests

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        for edge in self.link_states:
            self.link_states[edge] = np.zeros(self.num_slots, dtype=int)
        self.current_request_index = 0
        return self.get_observation(), {}

    def step(self, action):
        path = self.paths[action]
        reward = 0
        req = self.traffic_requests[self.current_request_index]
        util = self.utilzle_link(path, req[2])

        if util:
            reward += 1
            print(f"Reward for {path} {req}")
        else:
            reward -= 1
            print(f"Failed at {path} {req}. No reward.")
        
        self.decreaseHoldTime()
        

        self.current_request_index += 1
        done = self.current_request_index >= len(self.traffic_requests)
        info = {}
        return self.get_observation(), reward, done, False, info

    def decreaseHoldTime(self):
        for edge in self.link_states:
            for slot in range(self.num_slots):
                if self.link_states[edge][slot] > 0:
                    self.link_states[edge][slot] -= 1
        
    
    def utilzle_link(self, path, ht):
        for slot in range(self.num_slots):
            allocated = True
            for i in range (len(path) - 1):
                edge = (path[i], path[i+1])
                if edge not in self.link_states:
                    edge = (path[i+1], path[i])
                if self.link_states[edge][slot] != 0:
                    allocated = False
                    break
            
            if allocated:
                for j in range(len(path) - 1):
                    edge = (path[j], path[j+1])
                    if edge not in self.link_states:
                        edge = (path[j+1], path[j])
                    self.link_states[edge][slot] = ht
                return True
        return False 

    def get_observation(self):
        obs = []
        for states in self.link_states.values():
            for state in states:
                obs.append(state)
        return np.array(obs)

