from typing import final
import numpy as np
import pandas as pd
from pulp import *
import itertools


def create_routes(region):

    # Initialisation of graph dictionary and routes list
    routes = []
    nodes = []

    for _,v in region.items():
        nodes.append(int(v))
    
    # Specifying the Woolworths Distribution Centre node (i.e. node that cycle starts and ends on)
    DC = nodes[-1]

    # Generating all possible routes for the conditions specified
    for n1 in nodes:
        for n2 in nodes:
            for n3 in nodes:
                for n4 in nodes:
                    if n1!=DC and n2!=DC and n3!=DC and n4!=DC and n1!=n2 and n2!=n3 and n3!=n4 and n1!=n3 and n1!=n4 and n2!=n4:
                        routes.append([DC, n1, n2, n3, n4, DC])
                        routes.append([DC, n1, n2, n3, DC])
                        routes.append([DC, n1, n2, DC])
                        routes.append([DC, n1, DC])
    
    final_routes = []
    for elem in routes:
        if elem not in final_routes:
            final_routes.append(elem)
    routes = final_routes

    print('\n')
    print('Number of Routes: ')
    print(len(routes))

    return routes


def route_matrix(routes, total_nodes):

    # Initialising matrix for each route
    route_matrix = np.zeros(shape=(total_nodes,len(routes)))
    
    # Saving a value of 1 to positions in the matrix
    # Rows correspond to node number and columns correspond to each route
    for route in routes:
        for node in route:
            route_matrix[node-1][routes.index(route)] = 1

    return route_matrix
    

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
    print('Region 1 Completed')
    reg2_routes = create_routes(reg2)
    print('Region 2 Completed')
    reg3_routes = create_routes(reg3)
    print('Region 3 Completed')
    reg4_routes = create_routes(reg4)
    print('Region 4 Completed')
    reg5_routes = create_routes(reg5)
    print('Region 5 Completed')
    reg6_routes = create_routes(reg6)
    print('Region 6 Completed')

    # Creating a route matrix from the routes
    #route_matrix = route_matrix(reg6_routes, reg6)