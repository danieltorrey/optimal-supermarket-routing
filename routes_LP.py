from typing import final
import numpy as np
import pandas as pd
from pulp import *
import itertools
import math


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
    

def cost_route(routes):
    
    # Reading in the durations data from the csv file
    durations = pd.read_csv('WoolworthsTravelDurations.csv')

    # Reading the dataset containg average pallete demand estimate
    average = pd.read_csv('WoolworthsStores.csv')

    # Initialising region route costs dictionary and route number variable
    route_costs = {}
    route_number = 1

    DC = 66

    for route in routes:

        # Initialising total duration required for route
        total_dur = 0

        for node in route:
            # Setting index of current node being scanned
            if total_dur == 0:
                i = route.index(node)
            else:
                i += 1 

            # Checking whether node is the last node in the route
            if i != len(route)-1:

                # Finding cost from current node to next node and adding to total route cost variable
                travel_dur = float(durations.loc[node-1][route[i+1]])/3600   # in hours

                # If destination node not DC, will read in the r
                if route[i+1] != DC:
                    pallet_dur = (average.loc[route[i+1]-1][1])*(7.5/60)
                else:
                    pallet_dur = 0

                # Duration is calculated from node to node and then added to total duration
                dur = travel_dur + pallet_dur
                total_dur += dur

        # Calculating cost for route
        if math.ceil(total_dur) >= 4:
            route_cost = 900
        else: 
            route_cost = math.ceil(total_dur) * 225

        # Calculating additional costs if time exceeds 4 hours
        if total_dur > 4:
            extra_dur = math.ceil(total_dur-4)
            route_cost = route_cost + (extra_dur * 275)

        # Appending individual route cost to region route costs dictionary
        route_costs[route_number] = route_cost
        # Incrementing route number
        route_number += 1

    return route_costs


def lp_region(region, region_no):
    
    # Creating all possible routes for each region from the conditions specified
    reg_routes = create_routes(region)

    # Creating route matrix to see if node is visited or not
    visit_matrix = route_matrix(reg_routes, region)

    # Creating cost matrix for each region
    reg_cost = cost_route(reg_routes)

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
    trucks = round(len(region))
    
    # Truck Constraint
    prob += lpSum([1*route_vars[i] for i in route_vars]) == trucks, "Truck Constraint"
        
    prob.writeLP('Routes.lp')

    prob.solve()

    sys.stdout = open("{}".format(region_no), "w")

    print("Status:", LpStatus[prob.status])

    for v in prob.variables():
        if v.varValue == 1.0:
            print(v.name, "=", v.varValue)

    print("Total Cost from Routes = ", value(prob.objective))

    sys.stdout.close()


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

    # Optimising the routes for each region
    reg1_lp = lp_region(reg1, 1)
    reg2_lp = lp_region(reg2, 2)
    reg3_lp = lp_region(reg3, 3)
    reg4_lp = lp_region(reg4, 4)
    reg5_lp = lp_region(reg5, 5)
    reg6_lp = lp_region(reg6, 6)