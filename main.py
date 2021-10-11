from typing import final
import numpy as np
import pandas as pd
from pulp import *
from itertools import permutations
import math
import re
import os


def initialise_regions(weekday):

     # Reading in the data from the csv file
    data = pd.read_csv('WoolworthsStores.csv')
    data = data[0:65]

    # Initialising dictionaries for each of the regions
    reg1, reg2, reg3, reg4, reg5, reg6 = {}, {}, {}, {}, {}, {}
    
    
    # Saving the store name and its corresponding region for each store to a dictionary
    for i in range(1,len(data)+1):
        store_name = str(data.iloc[i-1]['Store'])
        region_number = int(data.iloc[i-1]['Region'])

        if weekday:
            store_demand = int(data.iloc[i-1]['Rounded Weekday'])
        else:
            store_demand = int(data.iloc[i-1]['Rounded Saturday'])
        
        if store_demand != 0:
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

    return reg1, reg2, reg3, reg4, reg5, reg6


def create_routes(region, length):

    # Initialisation of routes lists
    routes = []
    
    # Saving the nodes in the region to an array
    nodes = []
    for _,v in region.items():
        nodes.append(int(v))
  
    # Generating all possible routes for the conditions specified
    for i in range(1,length+1):
        perm = permutations(nodes, i)
        for j in perm:
            routes.append(list(j))

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
    

def cost_routes(routes, weekday):
    
    # Reading in the durations data from the csv file
    durations = pd.read_csv('WoolworthsTravelDurations.csv')
   
    # Reading the dataset containg average pallet demand estimates
    demand = pd.read_csv('WoolworthsStores.csv')
    demand = demand[0:66]
    
    # Initialising region route costs dictionary and route number variable
    route_costs = {}
    route_number = 1
    DC = 65
    
    for route in routes:

        # Initialising total duration required for route
        total_dur = 0
        route_demand = 0

        for node in route:
            node_demand = 0
            travel_dur = 0

            if len(route) > 1 and node != route[len(route)-1]:
                # Finding cost from current node to next node and adding to total route cost variable
                travel_dur = float(durations.loc[node-1][route[route.index(node)+1]]) / 3600  # in hours
           
            if weekday:
                node_demand = demand.loc[node-1][3]
            else:
                node_demand = demand.loc[node-1][2]

            route_demand += node_demand
            pallet_dur = node_demand * (7.5/60)

            # Duration is calculated from node to node and then added to total duration
            dur = travel_dur + pallet_dur
            total_dur += dur

        # Adding travel durations from DC to start node and and end node to DC
        total_dur += (float(durations.loc[DC][route[0]]) + float(durations.loc[route[-1]-1][DC+1])) / 3600
      
        # Calculating cost for route
        if total_dur > 4:
            route_cost = 900+(total_dur-4)*275 
        else: 
            route_cost = total_dur*225

        # Appending individual route cost to region route costs dictionary
        route_costs[route_number] = route_cost

        # Incrementing route number
        route_number += 1
   
    return route_costs


def optimise_routes(region, region_no, length, weekday):
    
    # Creating all possible routes for each region from the conditions specified
    reg_routes = create_routes(region, length)
    
    # Creating route matrix to see if node is visited or not
    visit_matrix = route_matrix(reg_routes, region)
    
    # Costing each route for each region
    reg_cost = cost_routes(reg_routes, time_period)
    
    # Setting up route variable for LP
    route = {}
    for k, v in reg_cost.items():
        route[k] = k
    
    # Generating LP
    prob = LpProblem("The Route Problem", LpMinimize)

    # Dictionary for Route variable in LP
    route_vars = LpVariable.dicts("Route", route, cat='Binary')
    
    # Objective function
    prob += lpSum([reg_cost[i]*route_vars[i] for i in route_vars]), "Route Optimisation Function"
    
    # Numbered list for node constraint
    num = list(range(1, len(route_vars)+1))

    # Constraint for each node to be visited once
    for row in range(np.shape(visit_matrix)[0]):
        con = pd.Series(visit_matrix[row], index = num)
        con_dict = dict(con)
        prob += lpSum([con_dict[i]*route_vars[i] for i in route_vars]) == 1, "Node_{}".format(row)
    
    # Calculating amount of truck routes available
    trucks = round((len(region)/65)*60)
    
    # Truck Constraint
    prob += lpSum([1*route_vars[i] for i in route_vars]) <= trucks, "Truck Constraint"   

    prob.solve()

    '''
    '''
    '''
    '''
    routes_id = {}
    for i in range(1,len(reg_routes)+1):
        routes_id[i] = reg_routes[i-1]

    os.chdir('results') 
    
    # Txt file to output LP results
    if weekday:
        os.chdir('weekday') 
        sys.stdout = open("LP Output - Region {}".format(region_no), "w")
    else:
        os.chdir('weekend') 
        sys.stdout = open("LP Output - Region {}".format(region_no), "w")

    print("Status:", LpStatus[prob.status])
    
    for v in prob.variables():
        if v.varValue == 1.0:
            print(v.name, "=", v.varValue)
    
    print("Total Cost from Routes = ", value(prob.objective))

    sys.stdout.close()

    # Txt file for actual route numbers
    if weekday:
        sys.stdout = open("Routes - Region {}".format(region_no), "w")
    else:
        sys.stdout = open("Routes - Region {}".format(region_no), "w")

    # To give route sequences
    for v in prob.variables():
        if v.varValue == 1.0:
            route_num = int(re.search(r'\d+', v.name).group())
            print(routes_id[route_num])

    sys.stdout.close()

    os.chdir('..')
    os.chdir('..')


if __name__ == "__main__":

    # True = weekday, False = weekend
    time_period = True 

    # Specifying max number of nodes that routes visit
    length = 4

    # Initialising regions depending on either weekday or weekend demand
    reg1, reg2, reg3, reg4, reg5, reg6 = initialise_regions(time_period) 
  
    # Optimising the routes for each region
    reg1_lp = optimise_routes(reg1, 1, length, time_period)
    reg2_lp = optimise_routes(reg2, 2, length, time_period)
    reg3_lp = optimise_routes(reg3, 3, length, time_period)
    reg4_lp = optimise_routes(reg4, 4, length, time_period)
    reg5_lp = optimise_routes(reg5, 5, length, time_period)
    reg6_lp = optimise_routes(reg6, 6, length, time_period)