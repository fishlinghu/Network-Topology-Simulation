# python3
import sys
import os

def parseAndExecute(filename_prefix, N):
    for num_switch_removed in range(1, N+1, 1):
    # for num_switch_removed in range(8, 9, 1):
        filename = filename_prefix + str(num_switch_removed) + ".txt"
        orig_server_idx_map = {}
        new_server_idx_map = {}
        old_new_idx_map = {}
        new_idx = 0

        with open(filename, 'r') as input_file, open("edge_list", 'w') as output_file:
            first_line_flag = True
            for line in input_file:
                if first_line_flag:
                    # first line is the list of server ids
                    for server_idx in line.split(' '):
                        orig_server_idx_map[int(server_idx)] = -1
                    first_line_flag = False
                else:
                    for old_idx in line.split(' '):
                        if int(old_idx) not in old_new_idx_map:
                            old_new_idx_map[int(old_idx)] = new_idx
                            new_idx = new_idx + 1
                        if int(old_idx) in orig_server_idx_map:
                            new_server_idx = old_new_idx_map[int(old_idx)]
                            new_server_idx_map[new_server_idx] = -1
                    output_file.write(line)

        input_file.close()
        output_file.close()

        #print(orig_server_idx_map)
        #print(new_server_idx_map)

        with open("server_file", 'w') as server_file:
            for key, _ in new_server_idx_map.items():
                server_file.write(str(key) + ' ')

        server_file.close()

        # complete the mapping
        # print(orig_server_idx_list)

        command = "./waf --run \"scratch/BisectionBW_robustness --input=edge_list --servers=server_file\""
        os.system(command)
        # print(command)
        os.remove("edge_list")
        os.remove("server_file")

def main():
    # usage: $script.py N num_of_servers
    # N = number of switches
    if len(sys.argv) != 3:
        print("usage: $python3 script.py N num_of_servers")
        return

    N = int(sys.argv[1])
    num_of_servers = int(sys.argv[2])

    # compute targeting attack
    filename_prefix = "ta_" + str(N) + "_" + str(num_of_servers) + "_"
    parseAndExecute(filename_prefix, N)

    # compute random attack
    filename_prefix = "rf_" + str(N) + "_" + str(num_of_servers) + "_"
    parseAndExecute(filename_prefix, N)

if __name__ == "__main__":
    main()
