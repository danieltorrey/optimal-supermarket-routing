import numpy as np
import pandas as pd
from pulp import *
from itertools import combinations


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

def route_matrix(paths, total_nodes):

    # Initialising matrix for each path
    route_matrix = np.zeros(shape=(total_nodes,len(paths)))
    
    for path in paths:
        for node in path:
            route_matrix[node-1][paths.index(path)] = 1

    return route_matrix
    

if __name__ == "__main__":

    data = pd.read_csv('WoolworthsStores.csv')
    data = data[1:66]

    reg1, reg2, reg3, reg4, reg5, reg6 = {}, {}, {}, {}, {}, {}

    for i in range(len(data)-1):
        store_name = str(data.iloc[i]['Store'])
        region_number = int(data.iloc[i]['Region'])
        
        if region_number == 1:
            reg1[store_name] = i+1
        elif region_number == 2:
            reg2[store_name] = i+1
        elif region_number == 3:
            reg3[store_name] = i+1
        elif region_number == 4:
            reg4[store_name] = i+1
        elif region_number == 5:
            reg5[store_name] = i+1
        else:
            reg6[store_name] = i+1

    # Initialisation of graph dictionary and cycles list
    graph = {}
    paths = []

    # Specifying the maxmimum amount of stores to be visited (excluding distribution centre)
    max_length = 1
    # Specifying the Woolworths Distribution Centre node (i.e. node that cycle starts and ends on)
    DC_node = 1
    # Specifying the number of nodes in region
    total_nodes = 10
    
    # Populating dictionary with edges to form a fully connected, undirected graph without self-loops
    for i in range(1,total_nodes+1):
        graph[i] = list(range(1,total_nodes+1))

    # Generating cycles for the conditions specified
    for node in graph:
        if (node == DC_node):
            for path in find_paths(graph, node, node):
                if (len(path) < max_length+2):
                    paths.append([node]+path)
    
    # Printing all possible paths
    print('\nPaths:') 
    print(paths)
    
    # Printing the number of all possible paths
    print('\nNumber of Paths:')
    print(str(len(paths)) + '\n')

    route_matrix = route_matrix(paths, total_nodes)
    print('Route Matrix:')
    print(route_matrix)