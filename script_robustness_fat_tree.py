# python3
import sys
import os


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
    for num_switch_removed in range(N, 0, -1):
        filename = filename_prefix + str(num_switch_removed) + ".txt"

        with open(filename, 'r') as input_file, open("edge_list", 'w') as output_file:
            first_line_flag = True
            for line in input_file:
                if first_line_flag:
                    # first line is the list of server ids
                    with open("server_file", 'w') as server_file:
                        server_file.write(line)
                    server_file.close()
                    first_line_flag = False
                else:
                    output_file.write(line)
        input_file.close()
        output_file.close()

        server_file = ""
        command = "./waf --run \"scratch/BisectionBW --input=edge_list --servers=server_file\""
        # os.system(command)
        # print(command)
        os.remove("edge_list")
        os.remove("server_file")

    # compute randomly attack
    """
    filename_prefix = "rf_" + str(N) + "_" + str(num_of_servers) + "_"
    for num_switch_remained in range(N, 0, -1):
        filename = filename_prefix + str(num_switch_remained) + ".txt"
        command = "./waf --run \"scratch/BisectionBW --input=scratch/" + filename + "\""
        os.system(command)
    """

if __name__ == "__main__":
    main()
