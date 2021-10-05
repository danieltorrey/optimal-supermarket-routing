from typing import final
import numpy as np
import pandas as pd
from pulp import *
import itertools


def create_routes(region):

    # Initialisation of routes and nodes lists
    routes = []
    nodes = []
    
    # Saving the nodes in the region to an array
    for _,v in region.items():
        nodes.append(int(v))
    
    # Specifying the Woolworths Distribution Centre node (i.e. node that cycle starts and ends on)
    DC = nodes.pop(-1)
    
    # Generating all possible routes for the conditions specified
    for n1 in nodes:
        for n2 in nodes:
            for n3 in nodes:
                for n4 in nodes:
                    # Preventing repeat nodes
                    if n1!=n2 and n2!=n3 and n3!=n4 and n1!=n3 and n1!=n4 and n2!=n4:
                        # Accounting for routes of lengths four or lower
                        if [DC, n1, n2, n3, n4, DC] not in routes:
                            routes.append([DC, n1, n2, n3, n4, DC])
                        if [DC, n1, n2, n3, DC] not in routes:
                            routes.append([DC, n1, n2, n3, DC])
                        if [DC, n1, n2, DC] not in routes:
                            routes.append([DC, n1, n2, DC])
                        if [DC, n1, DC] not in routes:
                            routes.append([DC, n1, DC])

    return routes


def route_matrix(routes, region):

    # Saving the nodes in the region to an array
    nodes = []
    for _,v in region.items():
        nodes.append(int(v))

    # Initialising matrix for each route
    route_matrix = np.zeros(shape=(len(nodes),len(routes)))
    
    # Saving a value of 1 to positions in the matrix
    # Rows correspond to node number and columns correspond to each route
    for route in routes:
        for node in route:
            route_matrix[nodes.index(node)][routes.index(route)] = 1

    return route_matrix
    

def cost_matrix(routes):
    
    # Reading in the durations data from the csv file
    durations = pd.read_csv('WoolworthsTravelDurations.csv')
    # Initialising region route costs dictionary and route number variable
    route_costs = {}
    route_number = 1

    for route in routes:
        # Initialising individual route cost variable
        route_cost = 0 

        for node in route:
            # Setting index of current node being scanned
            i = route.index(node)

            # Checking whether node is the last node in the route
            if i != len(route)-1:
                # Finding cost from current node to next node and adding to total route cost variable
                cost = durations.loc[node-1][route[i+1]]
                route_cost += cost
        
        # Appending individual route cost to region route costs dictionary
        route_costs[route_number] = route_cost
        # Incrementing route number
        route_number += 1

    return route_costs


if __name__ == "__main__":

    # Reading in the data from the csv file
    data = pd.read_csv('WoolworthsStores.csv')
    data = data[0:66]

    # Initialising dictionaries for each of the regions
    reg1, reg2, reg3, reg4, reg5, reg6 = {}, {}, {}, {}, {}, {}

    # Saving the store name and its corresponding region for each store to a dictionary
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
        # Saving the distribution centre node as the last node in each region
        elif region_number == 7:
            reg1[store_name] = i
            reg2[store_name] = i
            reg3[store_name] = i
            reg4[store_name] = i
            reg5[store_name] = i
            reg6[store_name] = i

    # Creating all possible routes for each region from the conditions specified
    reg1_routes = create_routes(reg1)

    print('\nRegion 1 Routes Completed')
    print('Number of Routes: ' + str(len(reg1_routes)) + '\n')

    reg1_cost = cost_matrix(reg1_routes)
    print(reg1_cost)

    #reg2_routes = create_routes(reg2)
    #print('Region 2 Routes Completed')
    #print('Number of Routes: ' + str(len(reg2_routes)) + '\n')
    
    #reg3_routes = create_routes(reg3)
    #print('Region 3 Routes Completed')
    #print('Number of Routes: ' + str(len(reg3_routes)) + '\n')

    #reg4_routes = create_routes(reg4)
    #print('Region 4 Routes Completed')
    #print('Number of Routes: ' + str(len(reg4_routes)) + '\n')

    #reg5_routes = create_routes(reg5)
    #print('Region 5 Routes Completed')
    #print('Number of Routes: ' + str(len(reg5_routes)) + '\n')

    #reg6_routes = create_routes(reg6)
    #print('Region 6 Routes Completed')
    #print('Number of Routes: ' + str(len(reg6_routes)) + '\n')

    # Creating route matrices from each of the routes for each region
    #reg1_route_matrix = route_matrix(reg1_routes, reg1)
    #print('Region 1 Route Matrix Completed')
    #reg2_route_matrix = route_matrix(reg2_routes, reg2)
    #print('Region 2 Route Matrix Completed')
    #reg3_route_matrix = route_matrix(reg3_routes, reg3)
    #print('Region 3 Route Matrix Completed')
    #reg4_route_matrix = route_matrix(reg4_routes, reg4)
    #print('Region 4 Route Matrix Completed')
    #reg5_route_matrix = route_matrix(reg5_routes, reg5)
    #print('Region 5 Route Matrix Completed')
    #reg6_route_matrix = route_matrix(reg6_routes, reg6)
    #print('Region 6 Route Matrix Completed')

    print('hello')