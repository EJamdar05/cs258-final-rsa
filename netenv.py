import gymnasium as gym
from gymnasium import spaces
import numpy as np
import networkx as nx
import random
import pandas as pd

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

        #True for scenario 2 and False for scenario 1
        self.isRandom = False
        #generate list of traffic requests (100)
        self.traffic_requests = self.generate_traffic_requests()
        #generate the shortest paths from traffic reqs
        self.paths = self.generate_paths()

        #action space is the total amount of paths to take
        self.action_space = spaces.Discrete(len(self.paths))
        print(len(self.paths))

        #observation_space is total amount of holding time per every link
        self.observation_space = spaces.Box(low=0, high=20, shape=(self.total_links * self.num_slots,), dtype=int)
        
        #index of the link states used in step
        self.current_request_index = 0

        #average util holds the average util per each edge
        self.average_util = {}
        for edge in self.graph.edges():
            self.average_util[edge] = []
        
    #generate paths will generate all short paths per each edge
    def generate_paths(self):
        paths = []
        #generate short path for SD->NJ
        if not self.isRandom:
            src = "San Diego Supercomputer Center"
            dst = "Jon Von Neumann Center, Princeton, NJ"
            paths = list(nx.shortest_simple_paths(self.graph, source=src, target=dst))
        else:
            #loop through every src dst nodes and get their paths
            for s, d, _, in self.traffic_requests:
                paths = paths + list(nx.shortest_simple_paths(self.graph, source=s, target=d))
        return paths

    #generate 100 traffic requests
    def generate_traffic_requests(self):
        requests = []
        nodes = list(self.graph.nodes()) 
        for i in range(100):
            #scenario 1
            if not self.isRandom:
                src = "San Diego Supercomputer Center"
                dst = "Jon Von Neumann Center, Princeton, NJ"
                ht = np.random.randint(10, 20) 
                requests.append((src, dst, ht))
            else:
                #scenario 2
                src, dst = random.sample(nodes, 2)  
                ht = np.random.randint(10, 20) 
                requests.append((src, dst, ht))
        return requests

    #reset the env
    def reset(self, seed=None, options=None):
        #save current average util to csv file
        if self.average_util.values():
            self.save_to_csv()
        #reset the env
        super().reset(seed=seed, options=options)
        #init all links to 0
        for edge in self.link_states:
            self.link_states[edge] = np.zeros(self.num_slots, dtype=int)
        #set the index of the req to 0
        self.current_request_index = 0
        #set average util for every edge to empty lists
        self.average_util = {}
        for edge in self.graph.edges():
            self.average_util[edge] = []
        return self.get_observation(), {}

    #action step
    def step(self, action):
        #get the path that was chosen
        path = self.paths[action]
        #set reward to 0
        reward = 0

        #get the current req at the curr index
        req = self.traffic_requests[self.current_request_index]
        #allocate the link
        util = self.utilzle_link(path, req[2])

        #if the link was utilized reward
        if util:
            reward = 1
            print(f"Reward for {path} {req}")
        #0 for if blocked
        else:
            reward = -1
            print(f"Failed at {path} {req}. No reward.")
        
        #decrease hold time for each edge
        self.decrease_hold_time()

        #increment index of the reqs
        self.current_request_index += 1

        #check if we have gone through all traffic reqs
        done = self.current_request_index >= len(self.traffic_requests)

        #calc avrg for all edges
        if(done):
            self.calc_average()
        info = {}
        return self.get_observation(), reward, done, False, info

    #decrease hold time for each slot in every edge if ht > 0
    def decrease_hold_time(self):
        for edge in self.link_states:
            for slot in range(self.num_slots):
                if self.link_states[edge][slot] > 0:
                    self.link_states[edge][slot] -= 1
    
    #calc average of all links and append to average_util
    def calc_average(self):
        for edge in self.link_states:
            self.average_util[edge].append(np.mean(self.link_states[edge]))
    
    #save average_util for every edge in the graph
    def save_to_csv(self):
        edge = []
        average = []

        for(src,dst), uses in self.average_util.items():
            label = f"{src}-{dst}"
            average_util = np.mean(uses) if uses else 0
            edge.append(label)
            average.append(average_util)
        
        data_frame = pd.DataFrame({
            "Edge": edge,
            "Average Utilization": average
        })

        data_frame.to_csv("/Users/eshaqjamdar/Desktop/cs258-final-project-rsa/results.csv", index=False)
        print("Saved to results.csv")
        
    
    #will attempt to allocate and use a slot
    def utilzle_link(self, path, ht):
        #loop through all total slots
        for slot in range(self.num_slots):
            #needed to prevent using slot that is used up
            allocated = True
            for i in range (len(path) - 1):
                #get the edge
                edge = (path[i], path[i+1])
                #if the edge is not present, flip the edge just in case
                #the edge conn is flipped 
                if edge not in self.link_states:
                    edge = (path[i+1], path[i])
                #return false if the slot is not free
                if self.link_states[edge][slot] != 0:
                    allocated = False
                    break
            #if the slot is free
            if allocated:
                #loop through the selected path
                for j in range(len(path) - 1):
                    #get the edge
                    edge = (path[j], path[j+1])
                    #flip edge just incase
                    if edge not in self.link_states:
                        edge = (path[j+1], path[j])
                    #assign hold time for the link
                    self.link_states[edge][slot] = ht
                return True
        return False 

    def get_observation(self):
        obs = []
        for states in self.link_states.values():
            for state in states:
                obs.append(state)
        return np.array(obs)

