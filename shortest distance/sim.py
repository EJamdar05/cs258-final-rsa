import csv
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random

class Request:
    """This class represents a request. Each request is characterized by source and destination nodes and holding time (represented by an integer).

    The holding time of a request is the number of time slots for this request in the network. You should remove a request that exhausted its holding time.
    """
    def __init__(self, s, t, ht):
        self.s = s
        self.t = t
        self.ht = ht

    def __str__(self) -> str:
        return f'req("{self.s}", "{self.t}", {self.ht})'

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        # used by set()
        return self.id


class EdgeStats:
    """This class saves all state information of the system. In particular, the remaining capacity after request mapping and a list of mapped requests should be stored.
    """
    def __init__(self, u, v, cap) -> None:
        self.id = (u,v)
        self.u = u
        self.v = v
        # remaining capacity
        self.cap = cap

        # spectrum state (a list of requests, showing color <-> request mapping). Each index of this list represents a color
        self.__slots = [None] * cap
        # a list of the remaining holding times corresponding to the mapped requests
        self.__hts = [0] * cap

    def __str__(self) -> str:
        return f'{self.id}, cap = {self.cap}'
        # return f'{self.id}, cap = {self.cap}: {self.reqs}'

    def add_request(self, req: Request, color:int):
        """update self.__slots by adding a request to the specific color slot

        Args:
            req (Request): a request
            color (int): a color to be used for the request
        """
        # update self.slots and self.hts
        self.__slots[color] = req
        self.__hts[color] = req.ht

        return

    def remove_requests(self):
        """update self.__slots by removing the leaving requests based on self.__hts; Also, self.__hts should be updated in this function.
        """
        for i in range(0, self.cap):    # iterate through cap
            self.__hts[i] -= 1          # subtract 1 from holding time
            if (self.__hts[i] <= 0):    # holding time ran out, remove request
                self.__hts[i] = 0
                self.__slots[i] = None

        return


    def get_available_colors(self) -> list[int]:
        """return a list of integers available to accept requests
        """
        open_colors = []

        for i in range(0, self.cap):    # iterate through cap
            if (self.__slots[i] == None):   # add color to list if open
                open_colors.append(i);

        return open_colors


    def show_spectrum_state(self):
        """Come up with a representation to show the utilization state of a link (by colors)
        """
        print("\tEdgeState: ", self)
        for i in range(0, self.cap):    # iterate through cap
            print(f"\tcolor:{i+1},\trequest:{self.__slots[i]},\tholding time:{self.__hts[i]}")   # print link states
        print("")

        return


def generate_requests(num_reqs: int, g: nx.Graph) -> list[Request]:
    """Generate a set of requests, given the number of requests and an optical network (topology)

    Args:
        num_reqs (int): the number of requests
        g (nx.Graph): network topology

    Returns:
        list[Request]: a list of request instances
    """
    request_list = []
    for i in range(num_reqs):   # generate num_reqs requests

        """
        # Case I
        source  = "San Diego Supercomputer Center"
        dest    = "Jon Von Neumann Center, Princeton, NJ"
        min_ht  = 10
        max_ht  = 20
        """


        #"""
        # Case II
        locations = random.sample([str(n) for n in G.nodes()], 2)   # pick two random locations from graph
        source  = locations[0]
        dest    = locations[1]
        min_ht  = 10
        max_ht  = 20
        #"""

        # Generate requests based on scenario
        h_time = np.random.randint(min_ht, max_ht)  # holding time
        r = Request(source, dest, h_time)           # create request
        request_list.append(r)                      # add to list

    return request_list


def generate_graph(string) -> nx.Graph:
    """Generate a networkx graph instance importing a GML file. Set the capacity attribute to all links based on a random distribution.

    Returns:
        nx.Graph: a weighted graph
    """
    return nx.read_gml(string)


def route(g: nx.Graph, estats: list[EdgeStats], req:Request) -> list[EdgeStats]:
    """Use a routing algorithm to decide a mapping of requests onto a network topology. The results of mapping should be reflected. Consider available colors on links on a path.

    Args:
        g (nx.Graph): a network topology
        req (Request): a request to map

    Returns:
        list[EdgeStats]: updated EdgeStats
    """

    # get request info
    source  = req.s
    dest    = req.t
    h_time  = req.ht
    # print("request: ", source, dest, h_time, "\n")

    # shortest path from source to dest
    nodes = nx.dijkstra_path(G, source, dest)
    """
    print("PATH:")
    for n in nodes:
        print(n)
    """

    # get edges on the way from source to dest
    edges = []
    for i in range(len(nodes) - 1):
        u = nodes[i]
        v = nodes[i + 1]
        edges.append((u,v))
    # print(edges, len(edges))

    # count which colors are avaible along the path
    color_dict = {}
    for e in estats:    # for edgestat
        (u, v) = (e.u, e.v)
        #print(f"'{u}', '{v}'")
        if ((u,v) in edges) or ((v,u) in edges):  # edge is part of shortest path
            # print(f"EDGE '{u}', '{v}'")
            open_colors = e.get_available_colors()
            for color in open_colors:   # track the number times a color occurs on the path
                if color in color_dict:
                    color_dict[color] += 1
                else:
                    color_dict[color] = 1

    # filter for colors that appear along the whole path
    viable_colors = {k:v for k,v in color_dict.items() if v == len(edges)}
    # print(viable_colors)

    if(len(viable_colors) > 0): # color exists
        picked_color = min(viable_colors.keys())
        data["blocking"] = 0
        # update route
        for e in estats:    # for edgestat
            (u, v) = (e.u, e.v)
            if ((u,v) in edges) or ((v,u) in edges):    # edge is part of shortest path
                e.add_request(req, picked_color)
    else:       # color does not exist along shortest path
        data["blocking"] = 1
        pass    # do nothing

    return estats


if __name__ == "__main__":
    # 1. generate a network
    """
    linear graph with 5 nodes
    (0)--(1)--(2)--(3)--(4)
    """
    """
    G = nx.Graph()
    G.add_edge(0,1)
    G.add_edge(1,2)
    G.add_edge(2,3)
    G.add_edge(3,4)
    """

    """
    Import GML file for graph.
    """
    G = generate_graph("nsfnet.gml")

    # print graph
    print("GRAPH:")
    for v,w in G.edges():
        print(v,w)
    print("\n\n")
    # nx.draw(G)
    # plt.show()


    # 2. generate a list of requests (num_reqs)
    # we simulate the sequential arrivals of the pre-generated requests using a for loop in this simulation
    requests = generate_requests(5, G)

    """
    # print requests
    print("\n\nREQUESTS:")
    for req in requests:
        print(req)
    print("\n\n")
    """

    # 3. prepare an EdgeStats instance for each edge.
    estats = []
    for u,v in G.edges():
        e = EdgeStats(u, v, 10)
        estats.append(e)

    # 4. this simulation follows the discrete event simulation concept. Each time slot is defined by an arrival of a request
    mydict = []     # data for csv
    time = 1
    for req in requests:
        print("--------------------------------------------------------------------")
        print("time slot: ", time)
        print("request: ", req.s, req.t, req.ht, "\n")
        data = {}
        data["time"] = time
        data2 = {}
        data2["time"] = time

        # 4.1 use the route function to map the request onto the topology (update EdgeStats)
        route(G, estats, req)

        # 4.2 remove all requests that exhausted their holding times (use remove_requests)
        for e in estats:
            e.remove_requests()
            e.show_spectrum_state()

            # data capture
            open_colors = len(e.get_available_colors())
            used_colors = 10 - open_colors
            util = used_colors / 10
            data[f"{e.id}"] = util

        mydict.append(data)
        time += 1

    # 5. write data out to csv file
    # credit to:
    # - https://www.geeksforgeeks.org/writing-csv-files-in-python/
    # - https://stackoverflow.com/questions/8746908/why-does-csv-file-contain-a-blank-line-in-between-each-data-line-when-outputting

    fields = ['time', 'blocking']
    for e in estats:
        fields.append(f"{e.id}")
    filename = "scenario.csv"
    # print(mydict)

    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=fields) # creating a csv dict writer object
        writer.writeheader()        # writing headers (field names)
        writer.writerows(mydict)    # writing data rows
