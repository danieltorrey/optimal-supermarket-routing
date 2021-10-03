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

#def path_to_matrix(graph, cycles, nodes):

    # Initialising cycles matrix list
    #cycles_matrix = []
    
    #for node in graph:
        # Initialising matrix for each path
        #matrix = np.zeros((total_nodes,total_nodes), int)

        #for i in range(total_nodes):
            #for j in cycles[i]:
                #matrix[i][j] = 1

        #cycles_matrix.append(matrix)
    

    
    #print(cycles_matrix)

    #return 
    

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
    cycles = []

    # Specifying the maxmimum amount of stores to be visited (excluding distribution centre)
    max_length = 4
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
                    cycles.append([node]+path)
    
    # Printing all possible cycles
    print('\nCycles:') 
    print(cycles)
    
    # Printing the number of all possible cycles
    print('\nNumber of Cycles:')
    print(str(len(cycles)) + '\n')

    #path_to_matrix(graph, cycles, total_nodes)