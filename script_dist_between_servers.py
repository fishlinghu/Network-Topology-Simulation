# python3
import sys
import os
import matplotlib.pyplot as plt
import networkx as nx

def readFileCreateGraph(filename):
    # create graph using networkx:
    edges = []
    with open(filename) as f:
        for line in f:
            line = line.split() # to deal with blank
            if line:            # lines (ie skip them)
                line = [int(i) for i in line]
                edges.append(line)
    f.close()

    G = nx.Graph()
    G.add_edges_from(edges)

    return G

def getListOfServers(G):
    server_list = []
    for idx in G.nodes():
        if G.degree(idx) == 1:
            server_list.append(idx)

    return server_list

def computeAvgDistBetweenServers(G, server_list):
    num_servers = len(server_list)

    counter = 0
    dist_sum = 0.0
    i = 0
    for i in range(num_servers):
        source_idx = server_list[i]
        for j in range(i+1, num_servers, 1):
            try:
                dist_sum = dist_sum + nx.shortest_path_length(G, source=source_idx, target=server_list[j])
                counter = counter + 1
            except:
                # print(sys.exc_info()[0])
                pass

    return dist_sum / counter

def main():
    # usage: $script.py filename
    if len(sys.argv) != 2:
        print("usage: $python3 script.py filename")
        return

    G = readFileCreateGraph(sys.argv[1])
    server_list = getListOfServers(G)
    avg_dist = computeAvgDistBetweenServers(G, server_list)
    print(avg_dist)


if __name__ == "__main__":
    main()
