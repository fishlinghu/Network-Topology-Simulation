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
    for num_switch_remained in range(N, 0, -1):
        filename = filename_prefix + str(num_switch_remained) + ".txt"
        command = "./waf --run \"scratch/BisectionBW --input=scratch/" + filename + "\""
        os.system(command)
        # print(command)

    # compute randomly attack
    filename_prefix = "rf_" + str(N) + "_" + str(num_of_servers) + "_"
    for num_switch_remained in range(N, 0, -1):
        filename = filename_prefix + str(num_switch_remained) + ".txt"
        command = "./waf --run \"scratch/BisectionBW --input=scratch/" + filename + "\""
        os.system(command)

if __name__ == "__main__":
    main()
