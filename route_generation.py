import numpy as np
import pandas as pd


def find_paths(graph, start, end):

    # Initialising paths list
    paths = [(start, [])]

    while paths:
        # Removing the top-most node from the paths list to initialise the current node being scanned and path being created
        current_node, path = paths.pop()

        # Checking whether the node has reached the end of the path
        if path and current_node == end:
            yield path
            continue
        
        # Checking whether the next node is in the path
        for next_node in graph[current_node]:
            # If so, repeat function
            if next_node in path:
                continue
            # If not, append current path to paths list
            paths.append((next_node, path+[next_node]))


if __name__ == "__main__":
    
    # Initialisation of graph dictionary and cycles list
    graph = {}
    cycles = []

    # Specifying length of cycle (i.e. how many nodes to be included in path)
    cycle_length = 5
    # Specifying the Woolworths Distribution Centre node (i.e. node that cycle starts and ends on)
    DC_node = 1
    # Specifying the number of nodes in region
    total_nodes = 10
    
    # Populating dictionary with edges to form a fully connected, undirected graph without self-loops
    for i in range(1,total_nodes+1):
        graph[i] = list(range(1,total_nodes+1))
        graph[i].pop(i-1)

    # Generating cycles for the conditions specified
    for node in graph:
        if (node == DC_node):
            for path in find_paths(graph, node, node):
                if (len(path) == cycle_length):
                    cycles.append([node]+path)
    
    # Printing all possible cycles
    print('\nCycles:') 
    print(cycles)
    
    # Printing the number of all possible cycles
    print('\nNumber of Cycles:')
    print(str(len(cycles)) + '\n')