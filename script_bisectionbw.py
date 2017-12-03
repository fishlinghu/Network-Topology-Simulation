# python3
import sys
import os
import matplotlib.pyplot as plt
import networkx as nx
import time

def plotServerBW(num_servers, bw, name, marker, label, title, color, filled_marker):
    # switches: fraction of switches removed
    # servers: fraction of servers reachable in largest component
    plt.figure(1)
    if filled_marker:
        plt.plot(num_servers, bw, color + '-', marker=marker, label=label)
    else:
        plt.plot(num_servers, bw, color + '-', marker=marker, label=label, mfc='none')
    # Shrink current axis by 25% for legend box
    plt.subplots_adjust(right=0.75)
    plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")

    plt.title(title)
    plt.xlabel("Number of servers supported")
    plt.ylabel("Bisection Bandwidth (Mbps)")
    plt.savefig(name)

def plotServerAvgDist(num_servers, avg_dist, name, marker, label, title, color, filled_marker):
    # switches: fraction of switches removed
    # servers: fraction of servers reachable in largest component
    plt.figure(2)
    if filled_marker:
        plt.plot(num_servers, avg_dist, color + '-', marker=marker, label=label)
    else:
        plt.plot(num_servers, avg_dist, color + '-', marker=marker, label=label, mfc='none')

    # Shrink current axis by 25% for legend box
    plt.subplots_adjust(right=0.75)
    plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")

    plt.title(title)
    plt.xlabel("Number of servers supported")
    plt.ylabel("Number of hops")
    plt.savefig(name)

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

def avgDistWrapper(filename):
    G = readFileCreateGraph(filename)
    server_list = getListOfServers(G)
    avg_dist = computeAvgDistBetweenServers(G, server_list)
    # print(avg_dist)

    return avg_dist

def simulateJellyfish(k, i):
    bw = []
    avg_dist = []
    N = int(5 * pow(k,2) / 4)
    fileprefix = "scratch/jellyfish_" + str(N) + "_" + str(k) + "_"
    for r in range(4, k, 2):
        filename = fileprefix + str(r) + "_0.txt";
        avg_dist.append(avgDistWrapper(filename))
        print(filename)
        command = "./waf --run \"scratch/BisectionBW --input=" + filename + "\""
        result = 0.0
        # repeat the experiment for i times
        for _ in range(i):
            os.system(command)
            result = result + readResult()

        # take average
        bw.append(result / i)
    return [avg_dist, bw]

def simulateFatTree(k, i):
    N = int(5 * pow(k,2) / 4)
    filename = "scratch/fat_tree_" + str(N) + "_" + str(k) + ".txt"
    avg_dist = avgDistWrapper(filename)
    print(filename)
    command = "./waf --run \"scratch/BisectionBW --input=" + filename + "\""
    result = 0.0
    # repeat the experiment for i times
    for _ in range(i):
        os.system(command)
        result = result + readResult()

    return [[avg_dist], [result / i]]

def readResult():
    bw = 0
    with open("result.txt", 'r') as simulation_result:
        for line in simulation_result:
            bw = float(line)

    os.remove("result.txt")
    return bw

def main():
    # usage: $script.py k i
    # N = number of switches
    # i = number of iterations
    if len(sys.argv) != 3:
        print("usage: $python3 script.py k i")
        return

    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    shape = ['s', 'o', '^', '8', 'v']
    counter = 0
    # draw many lines with different k

    for k in range(11, 16, 1):
        i = int(sys.argv[2])
        N = int(5 * pow(k,2) / 4)

        print("")
        print("++++++ k = " + str(k) + " ++++++")
        start = time.time()
        # start the simulation
        fat_tree_simulation_result = simulateFatTree(k, i)
        mid = time.time()
        print("  - Fat tree simulation time: " + str(mid-start) + " secs")
        jellyfish_simulation_result = simulateJellyfish(k, i)
        print("  - Jellyfish simulation time: " + str(time.time()-mid) + " secs")

        # get the result of average distance
        fat_tree_avg_dist = fat_tree_simulation_result[0]
        jellyfish_avg_dist = jellyfish_simulation_result[0]

        # get the list of bandwidth for y axis
        fat_tree_bw = fat_tree_simulation_result[1]
        jellyfish_bw = jellyfish_simulation_result[1]

        # get the list of number of servers for x axis
        fat_tree_num_servers = [pow(k, 3) / 4]
        jellyfish_num_servers = []
        for r in range(4, k, 2):
            jellyfish_num_servers.append((k - r) * N)

        plotServerBW(
            jellyfish_num_servers,
            jellyfish_bw,
            "ALL_bw.png",
            shape[counter],
            'JF-N='+str(N),
            'Maximum bisection bandwidth supported by different topologies',
            color[counter],
            True
        )
        plotServerBW(
            fat_tree_num_servers,
            fat_tree_bw,
            "ALL_bw.png",
            shape[counter],
            'FT-N='+str(N),
            'Maximum bisection bandwidth supported by different topologies',
            color[counter],
            False
        )

        plotServerAvgDist(
            jellyfish_num_servers,
            jellyfish_avg_dist,
            "ALL_avg_dist.png",
            shape[counter],
            'JF-N='+str(N),
            'Average distance between servers',
            color[counter],
            True
        )
        plotServerAvgDist(
            fat_tree_num_servers,
            fat_tree_avg_dist,
            "ALL_avg_dist.png",
            shape[counter],
            'FT-N='+str(N),
            'Average distance between servers',
            color[counter],
            False
        )
        counter = counter + 1

    ######################################################
    """
    k = int(sys.argv[1])
    i = int(sys.argv[2])
    N = int(5 * pow(k,2) / 4)

    # start the simulation
    fat_tree_simulation_result = simulateFatTree(k, i)
    jellyfish_simulation_result = simulateJellyfish(k, i)

    # get the result of average distance
    fat_tree_avg_dist = fat_tree_simulation_result[0]
    jellyfish_avg_dist = jellyfish_simulation_result[0]

    # get the list of bandwidth for y axis
    fat_tree_bw = fat_tree_simulation_result[1]
    jellyfish_bw = jellyfish_simulation_result[1]

    # get the list of number of servers for x axis
    fat_tree_num_servers = [pow(k, 3) / 4]
    jellyfish_num_servers = []
    for r in range(4, k, 2):
        jellyfish_num_servers.append((k - r) * N)

    print(fat_tree_num_servers)
    print(jellyfish_num_servers)
    print(fat_tree_bw)
    print(jellyfish_bw)

    plotServerBW(
        jellyfish_num_servers,
        jellyfish_bw,
        str(N) + "_" + str(k) + "_bw.png",
        'o',
        'jellyfish',
        'Maximum bisection bandwidth supported by different topologies',
        color[0]
    )
    plotServerBW(
        fat_tree_num_servers,
        fat_tree_bw,
        str(N) + "_" + str(k) + "_bw.png",
        's',
        'fat tree',
        'Maximum bisection bandwidth supported by different topologies',
        color[0]
    )

    plotServerAvgDist(
        jellyfish_num_servers,
        jellyfish_avg_dist,
        str(N) + "_" + str(k) + "_avg_dist.png",
        'o',
        'jellyfish',
        'Average distance between servers',
        color[0]
    )
    plotServerAvgDist(
        fat_tree_num_servers,
        fat_tree_avg_dist,
        str(N) + "_" + str(k) + "_avg_dist.png",
        's',
        'fat tree',
        'Average distance between servers',
        color[0]
    )
    """

if __name__ == "__main__":
    main()
