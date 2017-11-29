from networkx import *
import matplotlib.pyplot as plt
import networkx as nx
import operator
import scipy.stats as stats
from heapq import nlargest
import sys
import random



def random_failures(G, N, num):
    # G: the topology generate from networkx
    # N: number of switches, also where the server node starts
    # num: number of servers in the topology
    switch_removed = set()   # keep track of switches removed
    portion_server_reachable = [] # fraction of server reachable in the largest component
    portion_switches_removed = [] # fraction of switches removed at each step

    portion_switches_removed.append(0) # initially no switch removed, so 100% servers are reachable
    portion_server_reachable.append(1)
    while len(switch_removed) < N:
        # randomly remove a switch:
        s = random.randint(0, N - 1)
        while s in switch_removed:  # if a chosen switch already removed, randomly choose another one
            s = random.randint(0, N - 1)

        G.remove_node(s)
        switch_removed.add(s)

        reachable_servers = find_server_reachable(G)
        portion_switches_removed.append(len(switch_removed)/(N * 1.0))
        portion_server_reachable.append(len(reachable_servers)/(num * 1.0))
        # output the edges and reachable servers after a switch is removed:
        filename = "rf_" + str(N) + "_" + str(num) + "_" + str(len(switch_removed)) + ".txt"
        output_edges(filename, G, reachable_servers)

    # plot the robustness:
    title = "random failures for " + str(N) + " switches and " + str(num) + " servers"
    name = "rf_" + str(N) + "_" + str(num) + ".png"
    robustness_plot(portion_switches_removed, portion_server_reachable, title, name, 1)



def targeted_attacks(G, N, num):
    # remove switch in decreasing order of degree
    portion_server_reachable = [] # fraction of server reachable in the largest component
    portion_switches_removed = [] # fraction of switches removed at each step

    portion_switches_removed.append(0)
    portion_server_reachable.append(1)
    for s in range(N):
        G.remove_node(s)
        reachable_servers = find_server_reachable(G)
        portion_switches_removed.append((s + 1)/(N * 1.0))
        portion_server_reachable.append(len(reachable_servers)/(num * 1.0))
        # output edges and reachable servers:
        filename = "ta_" + str(N) + "_" + str(num) + "_" + str(s + 1) + ".txt"
        output_edges(filename, G, reachable_servers)

    # plot the robustness:
    title = "targeted attacks for " + str(N) + " switches and " + str(num) + " servers"
    name = "ta_" + str(N) + "_" + str(num) + ".png"
    robustness_plot(portion_switches_removed, portion_server_reachable, title, name, 2)



def find_server_reachable(G):
    # component_list: the connected components of a graph G
    # return the list of reachable servers in the component with max number of servers
    component_list = nx.connected_components(G)
    max_component = []

    for component in component_list:
        current_component = []
        for node in component:
            if node >= N:
                current_component.append(node)

        if len(current_component) > len(max_component):
            max_component = current_component

    return max_component



def output_edges(filename, G, reachable_servers):
    # print the current edges in the graph and the reachable servers in the last line
    with open(filename, 'w') as output:
        edges = G.edges()
        # first line is all available servers
        output.write(' '.join(str(server) for server in reachable_servers) + '\n')
        # the rest are edges list
        for edge in edges:
            output.write(str(edge[0]) + ' ' + str(edge[1]) + '\n')
    output.close()



def robustness_plot(switches, servers, title, name, i):
    # switches: fraction of switches removed
    # servers: fraction of servers reachable in largest component
    plt.figure(i)
    plt.plot(switches, servers,'b-', marker='o')
    plt.title(title)
    plt.xlabel("fraction of switches removed")
    plt.ylabel("fraction of servers reachable")
    plt.savefig(name)
    #plt.show()


####################################################################################################

if (len(sys.argv) == 1):
    print "python topology_robustness.py jellyfish_edges_filename k_value r_value"
    print "python topology_robustness.py fat-tree_edges_filename k_value"
    exit()


file = sys.argv[1]
k = int(sys.argv[2])
N = 5 * pow(k, 2) / 4
num = 0
if (len(sys.argv) == 3):  # fat-tree topology
    num = pow(k, 3) / 4
elif (len(sys.argv) == 4): # jellyfish topology
    r = int(sys.argv[3])
    num = N * (k - r)

print str(N) + " switches  " + str(num) + " servers"


# create graph using networkx:
edges = []
with open(file) as f:
    for line in f:
        line = line.split() # to deal with blank
        if line:            # lines (ie skip them)
            line = [int(i) for i in line]
            edges.append(line)
f.close()

G = nx.Graph()
G2 = nx.Graph()
G.add_edges_from(edges)
G2.add_edges_from(edges)


random_failures(G, N, num)
targeted_attacks(G2, N, num)
