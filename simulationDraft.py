from typing import final
import numpy as np
import pandas as pd
from pulp import *
from itertools import permutations
import math
import re
import os

from Lab6 import C

def initialise_regions(weekday):

    # Reading in the data from the csv file
    data = pd.read_csv('WoolworthsStores.csv')
    data = data[0:65]

    # Initialising dictionaries for each of the regions
    reg1, reg2, reg3, reg4, reg5, reg6 = {}, {}, {}, {}, {}, {}

    # Saving the store name and its corresponding region for each store to a dictionary
    for i in range(1, len(data)+1):
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
    for _, v in region.items():
        nodes.append(int(v))

    # Generating all possible routes for the conditions specified
    for i in range(1, length+1):
        perm = permutations(nodes, i)
        for j in perm:
            routes.append(list(j))

    return routes


def route_matrix(routes, region):

    # Saving the nodes in the region to an array
    nodes = []
    for _, v in region.items():
        nodes.append(int(v))

    # Initialising matrix for each route
    route_matrix = np.zeros(shape=(len(nodes), len(routes)))

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
    demand = pd.read_csv('WoolWorthsDemands.csv')
    demand = demand[0:66]

    # Initialising region route costs dictionary and route number variable
    route_costs = {}
    route_number = 1
    DC = 65

    def generateNodeDemand(node, weekday):

        # Get average demand and standard deviation, and generate random
        # variation for demand from normal distribution 
        if weekday == True:
            node_average = demand.loc[node-1][2]
            node_stddev = demand.loc[node-1][4]
            node_demand = np.random.normal(node_average, node_stddev) 
        else:
            node__average = demand.loc[node-1][1] 
            node_stddev = demand.loc[node-1][3]
            node_demand = np.random.normal(node_average, node_stddev) 

        return node_demand

    def generateTravelDuration(node, weekday): 

    # Using information adapted from Auckland Transport traffic counts
    # https://at.govt.nz/about-us/reports-publications/traffic-counts/
    #   - there is ~ 8624 vehicles on average on a Weekday
    #   - there is ~ 7524 vehicles on average on a Saturday

    # https://www.transport.govt.nz/assets/Uploads/Report/The-Congestion-Question-Report.pdf
    #   - "motorists now need to allow an additional 40 to 55 percent more time for their 
    #      trips to be assured of arriving on time"

        # Get travel duration from current node to next node
        if weekday: 
            # MAKE SOME TRAVEL TIME ADJUSTMENT (traffic_adj)
            travel_dur = float(
                durations.loc[node-1][route[route.index(node)+1]]) / 3600  # in hours
        else: 
            # MAKE SOME OTHER TRAVEL TIME ADJUSTMENT (traffic_adj)
            travel_dur = float(
                durations.loc[node-1][route[route.index(node)+1]]) / 3600  # in hours

        # Assume there is one peak hour of traffic during each four hour shift 
        # where motorists need to allow 55% more time for travel
        traffic_adj = (travel_dur / 4) * 1.55 

        # Add traffic adjustment to travel duration 
        travel_dur += traffic_adj 
        
        return travel_dur 


    def generateTravelDurationDC(weekday): 
    
        # Similar function for travel duration from DC to start node and end node to DC 

        if weekday: 
            # MAKE SOME TRAVEL TIME ADJUSTMENT (traffic_adj)
            DC_travel_dur =  (float(durations.loc[DC][route[0]]) +
                                float(durations.loc[route[-1]-1][DC+1])) / 3600
        else: 
            # MAKE SOME OTHER TRAVEL TIME ADJUSTMENT (traffic_adj)
            DC_travel_dur = (float(durations.loc[DC][route[0]]) +
                                float(durations.loc[route[-1]-1][DC+1])) / 3600

        # Assume there is one peak hour of traffic during each four hour shift 
        # where motorists need to allow 55% more time for travel
        traffic_adj = (travel_dur / 4) * 1.55

        # Add traffic adjustment to travel duration
        DC_travel_dur += traffic_adj 

        return DC_travel_dur

    for route in routes:

        # Initialising total duration required for route
        total_dur = 0
        route_demand = 0

        for node in route:
            node_demand = 0
            node_average = 0
            node_stddev = 0
            travel_dur = 0

            if weekday:
                node_demand = generateNodeDemand(node, weekday=True)
                if len(route) > 1 and node != route[len(route)-1]:
                    travel_dur = generateTravelDuration(node, weekday=True)
            else:
                node_demand = generateNodeDemand(node, weekday=False) 
                if len(route) > 1 and node != route[len(route)-1]:
                    travel_dur = generateTravelDuration(node, weekday=False)               

            route_demand += node_demand
            pallet_dur = node_demand * (7.5/60)

            # Duration is calculated from node to node and then added to total duration
            dur = travel_dur + pallet_dur
            total_dur += dur

        # Adding travel duration for DC to start node and end node to DC
        if weekday:
            total_dur += generateTravelDurationDC(weekday=True)
        else:
            total_dur += generateTravelDurationDC(weekday=False) 

        # Calculating cost for route
        if total_dur > 4:
            route_cost = 900+(total_dur-4)*275
        else:
            route_cost = total_dur*225

        if route_demand > 26:
            route_cost = 999999

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
    prob += lpSum([reg_cost[i]*route_vars[i]
                   for i in route_vars]), "Route Optimisation Function"

    # Numbered list for node constraint
    num = list(range(1, len(route_vars)+1))

    # Constraint for each node to be visited once
    for row in range(np.shape(visit_matrix)[0]):
        con = pd.Series(visit_matrix[row], index=num)
        con_dict = dict(con)
        prob += lpSum([con_dict[i]*route_vars[i]
                       for i in route_vars]) == 1, "Node_{}".format(row)

    # Calculating amount of truck routes available
    trucks = round((len(region)/65)*60)

    # Truck Constraint
    prob += lpSum([1*route_vars[i]
                   for i in route_vars]) <= trucks, "Truck Constraint"

    # Solve and suppress output 
    prob.solve(PULP_CBC_CMD(msg=0))

    return prob.objective.value()


# Evaluate routing schedule costs

# True = weekday, False = weekend
time_period = True

# Specify max number of nodes that routes visit
length = 4

# Initialise regions depending on either weekday or weekend demand
reg1, reg2, reg3, reg4, reg5, reg6 = initialise_regions(time_period)

# Optimal route costs already obtained (2dp) for each region 
if time_period == True: 
    optimisedCosts = [3047.00, 2750.47, 3348.99, 2623.63, 3213.96, 3310.85] # weekday solutions
else: 
    optimisedCosts = [2190.65, 1570.52, 1861.98, 1205.50, 1819.53, 1814.06] # weekend solutions

# Initialise matrices for simulations (run 10 times)
expectedTimes = np.zeros((6,10))
completionTimes = np.zeros((6,10))

# Carry out simulations 
for i in range(len(completionTimes.shape[0])):
    for j in range(len(completionTimes.shape[1])): 
        
        # Set expected times for each region 
        expectedTimes[i][j] = optimisedCosts[i]

        # Region 1 Simulation 
        completionTimes[0][j] = round(optimise_routes(reg1, 1, length, time_period),2)

        # Region 2 Simulation 
        completionTimes[1][j] = round(optimise_routes(reg2, 2, length, time_period),2)

        # Region 3 Simulation 
        completionTimes[2][j] = round(optimise_routes(reg3, 3, length, time_period),2)

        # Region 4 Simulation 
        completionTimes[3][j] = round(optimise_routes(reg4, 4, length, time_period),2)
        
        # Region 5 Simulation 
        completionTimes[4][j] = round(optimise_routes(reg5, 5, length, time_period),2)

        # Region 6 Simulation 
        completionTimes[5][j] = round(optimise_routes(reg6, 6, length, time_period),2)

        # # Region 1 Simulation
        # ExpectedTimes_1[i] = optimisedCosts[j]
        # CompletionTimes_1[i] = round(optimise_routes(reg1, 1, length, time_period),2)

print(expectedTimes)
print(completionTimes)

# Can edit and use the following as necessary

# Histograms
# plt.hist(CompletionTimes, density=True, histtype='stepfilled', alpha=0.2)
# plt.hist(ExpectedTimes, density=True, histtype='stepfilled', alpha=0.2)

# Average completion time
# np/mean(CompletionTimes_x)

# One sample t-test, which H0 = expected completion time
# print(stats.ttest_1samp(CompletionTimes_x, 24.67))

# Percentile interval
# CompletionTimes_x.sort()
# lowerBound = CompletionTimes_x[25]
#upperBound = CompletionTimes_x[975]

# Error rate
# errorRate = sum(np.greater(CompletionTimes_x, ExpectedTimes_x))/len(CompletionTimes)
