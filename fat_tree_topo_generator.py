'''
# given an even k, which is number of ports in for each switch (equivelent to k in Jellyfish topology)
# generate a three-tier level fat-tree with:
# N = (5/4)k^2 switches (three type of switches: core, aggregation, and edge switches)
# (k^3)/4 servers
'''

import sys

def fat_tree_topology(k):
    N = 5 * pow(k,2) / 4  # total number of switches
    core_num = pow(k, 2) / 4 # number of core switches: range from 0 to core_num
    agg_num = pow(k, 2) / 2  + core_num  # upper bound for aggregation switches; range from core_num to agg_num
    edge_num = pow(k, 2) / 2 + agg_num # upper bound for edge switches; range from agg_num to edge_num
    server_num = pow(k, 3) / 4  + edge_num # upper bound for servers: servers range from edge_num to server_num
    #print str(N) + ' ' + str(core_num) + ' ' + str(agg_num) + ' ' + str(edge_num) + ' ' + str(server_num)
    filename = 'fat_tree' + '_' + str(N) + '_' + str(k) + '.txt'

    with open(filename, 'w') as output:
        # create link between core switch and aggregation switch:
        temp = 0
        temp2 = core_num
        for temp_core in range(0, core_num, k/2):
            #temp = temp_core
            #print 'temp_core: ' + str(temp_core) + ' temp: ' + str(temp)
            for core in range(temp_core, temp_core + k/2):
                #print 'core: ' + str(core) + '  temp2: ' + str(temp2)
                for agg in range(temp2, agg_num, k/2):
                    #print 'agg: ' + str(agg)
                    output.write(str(core) + ' ' + str(agg) + '\n')
                    #print (agg)

            temp2 += 1

        # create link between aggregation switch and edge switch:
        len = 0
        for pord in range (core_num, agg_num, k/2):
            for agg in range(pord, pord + k/2):
                temp = agg_num + len * (k/2)
                for edge_switch in range(temp, temp + k/2):
                    output.write(str(agg) + ' ' + str(edge_switch) + '\n')
            len+=1


        # create link between edge switch and server:
        temp = edge_num
        for edge_switch in range(agg_num, edge_num):
            for server in range (temp, temp + k/2):
                output.write(str(edge_switch) + ' ' + str(server) + '\n')
            temp += k/2

    output.close()

    print 'Fat-tree: ' + str(N) + ' switches,' + str(pow(k,3)/4) + ' servers for k = ' + str(k) + '.\nThe node number of servers is from ' + str(edge_num) + ' to ' + str(server_num - 1) + ' (inclusive).\n'

    return


###########################################################################################
'''
# to run in terminal: python fat_tree_topology.py k_value
# NOTE: k_value should be be even number
'''

if (len(sys.argv) > 1):
    k = int(sys.argv[1])
    fat_tree_topology(k)

#fat_tree_topology(22)




