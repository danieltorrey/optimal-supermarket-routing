import numpy as np
import pandas as pd


def find_all_paths(graph, start, end):
    paths = [(start, [])]
    while paths:
        state, path = paths.pop()
        if path and state == end:
            yield path
            continue
        for next_state in graph[state]:
            if next_state in path:
                continue
            paths.append((next_state, path+[next_state]))


if __name__ == "__main__":
    
    # Initialisation of graph dictionary and cycles list
    graph = {}
    cycles = []

    # Specifying length of cycle (i.e. how many nodes to be included in path)
    cycle_length = 5
    # Specifying the Woolworths Distribution Centre node (i.e. node that cycle starts and ends on)
    DC_node = 1
    
    # Populating dictionary with edges to form a fully connected, undirected graph
    for i in range(1,11):
        graph[i] = list(range(1,11))
        graph[i].pop(i-1)

    # Generating cycles for the conditions specified
    for node in graph:
        if (node == DC_node):
            for path in find_all_paths(graph, node, node):
                if (len(path) == cycle_length):
                    cycles.append([node]+path)
    
    # Printing all possible cycles
    print('\nCycles:') 
    print(cycles)
    
    # Printing the number of all possible cycles
    print('\nNumber of Cycles:')
    print(str(len(cycles)) + '\n')