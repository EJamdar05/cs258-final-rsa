import gymnasium as gym
from gymnasium import spaces
import numpy as np
import networkx as nx
import random

class NetworkEnvironment(gym.Env):

    def __init__(self) -> None:
        super().__init__()
        self._graph = nx.read_gml('nsfnet.gml')

        # define state space
        e = len(self._graph.edges())  # number of edges in graph
        self.observation_space = spaces.Dict(
            {
            "links": spaces.Box(0, 10, shape=(e,), dtype=int),
            "holding times": spaces.Box(0, 20, shape=(e,10,), dtype=int),
            "req": spaces.Box(0, e-1, shape=(2,), dtype=int),
            "ht": spaces.Box(10, 20, shape=(1,), dtype=int),
            }
        )

        # set data arrays of linkstates and holding times
        self._linkstates    = np.array([0] * e)         # 1 x 15 empty array
        self._holdingtimes  = np.array([[0] * 10] * e)  # 10 x 15 empty array

        # get request and holding time
        self._req   = self._generate_req()
        self._ht    = self._generate_ht()

        # get start and end names from req
        start   = self._req[0]
        end     = self._req[1]
        i = 0
        for n in self._graph.nodes():     # iterate through nodes
            if i == start:  # get start name
                start = n
            elif i == end:  # get end name
                end = n
            else:           # do nothing otherwise
                pass
            i += 1

        # get paths from source to dest
        paths = list(nx.shortest_simple_paths(self._graph, start, end))
        p = len(paths)  # number of paths

        # define action space
        self.action_space = spaces.Discrete(p+1)    # number of paths + 1 blocking
        self.round = 0
        return None


    def _generate_req(self):
        locations = random.sample(list(range(13)), 2)
        # return np.array([locations[0] , locations[1]])  # scenario II
        return np.array([7 , 1])                        # scenario I


    def _generate_ht(self):
        return np.array([np.random.randint(10, 20+1),])


    def _get_obs(self):
        return {
            "links": self._linkstates,
            "holding times": self._holdingtimes,
            "req": self._req,
            "ht": self._ht
        }


    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)

        e = len(self._graph.edges())  # number of edges in graph

        # reset data arrays of linkstates and holding times
        self._linkstates    = np.array([0] * e)         # 1 x 15 empty array
        self._holdingtimes  = np.array([[0] * 10] * e)  # 10 x 15 empty array

        # get request and holding time
        self._req   = self._generate_req()
        self._ht    = self._generate_ht()

        # get start and end names from req
        start   = self._req[0]
        end     = self._req[1]
        i = 0
        for n in self._graph.nodes():     # iterate through nodes
            if i == start:  # get start name
                start = n
            elif i == end:  # get end name
                end = n
            else:           # do nothing otherwise
                pass
            i += 1

        # get paths from source to dest
        paths = list(nx.shortest_simple_paths(self._graph, start, end))
        p = len(paths)  # number of paths

        # define action space
        self.action_space = spaces.Discrete(p+1)    # number of paths + 1 blocking
        self.round = 0

        # return observation and info
        observation = self._get_obs()
        info = {}

        return observation, info


    def step(self, action):
        # action = 0 - (n-1) (select path), n = blocking

        # get start and end names from req
        start   = self._req[0]
        end     = self._req[1]
        i = 0
        for n in self._graph.nodes():     # iterate through nodes
            if i == start:  # get start name
                start = n
            elif i == end:  # get end name
                end = n
            else:           # do nothing otherwise
                pass
            i += 1

        # get paths from source to dest
        paths = list(nx.shortest_simple_paths(self._graph, start, end))
        p = len(paths)  # number of paths

        # define blocking actions and reward
        blocking_action = p     # 0 - p-1 are path selection
        blocking_reward = -1

        # check if terminate
        self.round += 1
        terminated = (self.round == 100) # True if it experienced 8 rounds

        # determine actions
        if action == blocking_action:
            # we need to block
            reward = blocking_reward
        else: # update edge stats

            # check if route possible
            # print(action)
            selected_path = paths[action]

            # get edges on path
            path_edges = []
            for i in range(len(selected_path) - 1):
                u = selected_path[i]
                v = selected_path[i + 1]
                path_edges.append((u,v))

            # count colors along path
            color_dict = {}
            for (u, v) in path_edges:
                #print(u,v)
                i = 0
                for e in self._graph.edges():
                    if ((u,v) == e) or ((v, u) == e):   # e in path
                        #print(i, e)
                        # count color in color dict
                        for c in range(10):
                            ht = self._holdingtimes[i , c]
                            #print(ht)
                            if ht == 0: # open color
                                if c in color_dict:
                                    color_dict[c] += 1
                                else:
                                    color_dict[c] = 1
                    # index through edges
                    i += 1

            viable_colors = {k:v for k,v in color_dict.items() if v == len(selected_path) - 1}

            # route
            if (len(viable_colors) > 0): # color exists
                picked_color = min(viable_colors.keys())    # greedy color picking
                for (u, v) in path_edges:
                    i = 0
                    for e in self._graph.edges():
                        if ((u,v) == e) or ((v, u) == e):   # e in path
                            self._linkstates += 1
                            self._holdingtimes[i, picked_color] = self._ht
                        i += 1
                reward = +1 * (len(selected_path) - 1)  # + number of edges affected
            else:   # color does not exist along path, block
                reward = blocking_reward


            # update based on holding time
            for i in range(len(self._graph.edges())):
                count = 0
                for j in range(10):
                    if self._holdingtimes[i, j] == 0:
                        count += 1
                    else:
                        self._holdingtimes[i, j] -= 1

                self._linkstates[i] = count



        self._req   = self._generate_req()
        self._ht    = self._generate_ht()
        observation = self._get_obs()
        info = {}

        # print(observation)

        return observation, reward, terminated, terminated, info
