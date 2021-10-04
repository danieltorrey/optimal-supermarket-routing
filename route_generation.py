import numpy as np
import pandas as pd
from pulp import *
from itertools import combinations


def create_routes(max_length, region):

    # Initialisation of graph dictionary and routes list
    graph = {}
    routes = []
    nodes = []

    for _,v in region.items():
        nodes.append(int(v))

    # Populating dictionary with edges to form a fully connected, undirected graph without self-loops
    for i in nodes:
        graph[i] = list(nodes)
    
    # Specifying the Woolworths Distribution Centre node (i.e. node that cycle starts and ends on)
    DC_node = nodes[-1]

    print('\n')
    print(nodes)
    print('\n')
    print(graph)
    print('\n')
    print(DC_node)

    # Generating all possible routes for the conditions specified
    for node in graph:
        if (node == DC_node):
            for route in find_routes(graph, node, node):
                if (len(route) < max_length):
                    routes.append([node]+route)
                    print(routes)
    
    return routes


def find_routes(graph, start, end):

    # Initialising routes list
    routes = [(start, [])]

    while routes:
        # Removing the top-most node from the routes list to initialise the current node being scanned and route being created
        current_node, route = routes.pop()

        # Checking whether the node has reached the end of the route
        if route and current_node == end:
            yield route
            continue
        
        # Checking whether the next node is in the route
        for next_node in graph[current_node]:
            # If so, repeat function
            if next_node in route:
                continue
            # If not, append current route to routes list
            routes.append((next_node, route+[next_node]))


def route_matrix(routes, total_nodes):

    # Initialising matrix for each route
    route_matrix = np.zeros(shape=(total_nodes,len(routes)))
    
    for route in routes:
        for node in route:
            route_matrix[node-1][routes.index(route)] = 1

    return route_matrix
    

if __name__ == "__main__":

    data = pd.read_csv('WoolworthsStores.csv')
    data = data[0:66]

    reg1, reg2, reg3, reg4, reg5, reg6 = {}, {}, {}, {}, {}, {}

    for i in range(1,len(data)+1):
        store_name = str(data.iloc[i-1]['Store'])
        region_number = int(data.iloc[i-1]['Region'])
        
        if region_number == 1:
            reg1[store_name] = i
        elif region_number == 2:
            reg2[store_name] = i
        elif region_number == 3:
            reg3[store_name] = i
        elif region_number == 4:
            reg4[store_name] = i
        elif region_number == 5:
            reg5[store_name] = i
        elif region_number == 6:
            reg6[store_name] = i
        elif region_number == 7:
            reg1[store_name] = i
            reg2[store_name] = i
            reg3[store_name] = i
            reg4[store_name] = i
            reg5[store_name] = i
            reg6[store_name] = i

    # Specifying the maxmimum amount of stores to be visited (excluding distribution centre)
    max_length = 1

    # Creating all possible routes for each region from the conditions specified
    #reg1_routes = create_routes(max_length, reg1)
    #reg2_routes = create_routes(max_length, reg2)
    #reg3_routes = create_routes(max_length, reg3)
    #reg4_routes = create_routes(max_length, reg4)
    #reg5_routes = create_routes(max_length, reg5)
    reg6_routes = create_routes(max_length, reg6)
    print('\nRoutes:') 
    print(reg6_routes)

    # Creating a route matrix from the routes
    #route_matrix = route_matrix(routes, reg6)

    # Printing the route matrix for each of the routes
    #print('Route Matrix:')
    #print(route_matrix)