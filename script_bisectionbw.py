# python3
import sys
import os
import matplotlib.pyplot as plt

def plotServerBW(num_servers, bw, name):
    # switches: fraction of switches removed
    # servers: fraction of servers reachable in largest component
    plt.figure(1)
    plt.plot(num_servers, bw,'b-', marker='o')
    # plt.title(title)
    plt.xlabel("Number of servers supported")
    plt.ylabel("Bisection Bandwidth (Mbps)")
    plt.savefig(name)

def simulateJellyfish(k, i):
    bw = []
    N = int(5 * pow(k,2) / 4)
    fileprefix = "scratch/jellyfish_" + str(N) + "_" + str(k) + "_"
    for r in range(4, k, 2):
        filename = fileprefix + str(r) + "_0.txt";
        print(filename)
        command = "./waf --run \"scratch/BisectionBW --input=" + filename + "\""
        result = 0.0
        # repeat the experiment for i times
        for _ in range(i):
            os.system(command)
            result = result + readResult()

        # take average
        bw.append(result / i)
    return bw

def simulateFatTree(k, i):
    N = int(5 * pow(k,2) / 4)
    filename = "scratch/fat_tree_" + str(N) + "_" + str(k) + ".txt"
    print(filename)
    command = "./waf --run \"scratch/BisectionBW --input=" + filename + "\""
    result = 0.0
    # repeat the experiment for i times
    for _ in range(i):
        os.system(command)
        result = result + readResult()

    return result / i

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

    k = int(sys.argv[1])
    i = int(sys.argv[2])
    N = int(5 * pow(k,2) / 4)

    # get the list of bandwidth for y axis
    fat_tree_bw = [simulateFatTree(k, i)]
    jellyfish_bw = simulateJellyfish(k, i)

    # get the list of number of servers for x axis
    fat_tree_num_servers = [pow(k, 3) / 4]
    jellyfish_num_servers = []
    for r in range(4, k, 2):
        jellyfish_num_servers.append((k - r) * N)

    print(fat_tree_num_servers)
    print(jellyfish_num_servers)
    print(fat_tree_bw)
    print(jellyfish_bw)

    plotServerBW(jellyfish_num_servers, jellyfish_bw, str(N) + "_" + str(k) + ".png")
    plotServerBW(fat_tree_num_servers, fat_tree_bw, str(N) + "_" + str(k) + ".png")


if __name__ == "__main__":
    main()
