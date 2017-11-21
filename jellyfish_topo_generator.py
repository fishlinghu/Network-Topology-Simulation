from networkx import *
import matplotlib.pyplot as plt
import networkx as nx
import sys


# create random r-regular graph using networkx
def jellyfish_topology(N, k, r, i):
    N = int(N) # number of switches
    k = int(k) # number of ports each switch has
    r = int(r) #number of ports in each switch to be connected to other switches
    i = int(i) # number of iteratives (for multiple testing purpose)
    if (N * r) % 2 != 0:
        print "please make sure N * r is even number."
        return None

    G = nx.random_regular_graph(r, N, None)  # only for N*r is even value
    edges = nx.edges(G)
    #filename = 'jellyfish_' + str(N) + '_' + str(k) + '_' + str(r) + '.txt'
    filename = 'jellyfish_' + str(N) + '_' + str(k) + '_' + str(r) + '_' + str(i) + '.txt'
    with open(filename, 'w') as output:
        for edge in edges:
            output.write(str(edge[0]) + ' ' + str(edge[1]) + '\n')

        # add switch-server connection:
        server_num = N  # total of N*(k-r) servers, server number range from N to N+N*(k-r)-1
        for s in range(N):   # each switch connect to (k - r) servers
            for p in range(k - r):
                output.write(str(s) + ' ' + str(server_num) + '\n')
                server_num += 1
    print 'Jellyfish: ' + str(N) + ' switches,' + str(N * (k - r)) + ' servers for k = ' + str(k) + ', r = ' + str(r) + '.\nThe node number of servers is from ' + str(N) + ' to ' + str(N + N * (k - r) - 1) + ' (inclusive).\n'

    output.close()
    return G



###########################################################################################
'''
# to run in terminal: python jellyfish_topology.py N_value k_value r_value i_value
# NOTE: k_value should be be even number
'''

if (len(sys.argv) > 4):
    N = sys.argv[1]
    k = sys.argv[2]
    r = sys.argv[3]
    i = sys.argv[4]
    jellyfish_topology(N, k, r, i)


#jellyfish_topology(20,4,2,2)

#nx.draw(G)
#plt.savefig("jellyfish_graph_20.png")


