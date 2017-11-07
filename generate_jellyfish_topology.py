from networkx import *
import matplotlib.pyplot as plt
import networkx as nx
import sys

# create random r-regular graph using networkx
def jellyfish_topology(N, k, r, i):
    # N = number of switches
    # k = number of ports each switch has
    # r = number of ports in each switch to be connected to other switches
    # i = number of iteratives (for multiple testing purpose)
    if (N * r) % 2 != 0:
        print("please make sure N * r is even number.")
        return None

    G = nx.random_regular_graph(r, N, None)  # only for N*r is even value
    edges = nx.edges(G)
    #filename = 'jellyfish_' + str(N) + '_' + str(k) + '_' + str(r) + '.txt'
    filename = 'jellyfish_' + str(N) + '_' + str(k) + '_' + str(r) + '_' + str(i) + '.txt'
    with open(filename, 'w') as output:
        for edge in edges:
            output.write(str(edge[0]) + ' ' + str(edge[1]) + '\n')

        # add switch-server connection:
        server_idx = N  # total of N*(k-r) servers, server number range from N to N+N*(k-r)-1
        print(N*(k-r), "servers there")
        for s in range(N):   # each switch connect to (k - r) servers
            for p in range(k - r):
                output.write(str(s) + ' ' + str(server_idx) + '\n')
                server_idx += 1
    output.close()
    print(filename, "generated")
    return G

def main():
    # usage: $script.py N k r i
    if len(sys.argv) != 5:
        print("usage: $python3 script.py N k r i")
        print("N k r i are positive integers")
        return

    N = int(sys.argv[1])
    k = int(sys.argv[2])
    r = int(sys.argv[3])
    i = int(sys.argv[4])

    for it in range(i):
        jellyfish_topology(N, k, r, it)

    #nx.draw(G)
    #plt.savefig("jellyfish_graph_20.png")

if __name__ == "__main__":
    main()
