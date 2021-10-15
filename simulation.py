from typing import final
import numpy as np
import pandas as pd
from pulp import *
from itertools import permutations
import os 
from scipy import stats
import matplotlib.pyplot as plt

def get_routes(weekday): 
    
    # Initialise route array
    routes = [] 
    
    # Get current directory 
    directory = os.getcwd()

    if weekday:     
        # Read in routes for each region from the 'weekday' folder
        for i in range (1, 7):
            # Get path for file name
            folder = (directory + os.sep + 'results' + os.sep + 'weekday')
            filename = folder + (os.sep + 'Routes - Region ' + str(i))
            # Open the file
            file = open(filename, 'r')
            # Add each route to the list of routes 
            routes += file.readlines()
            # Close file 
            file.close()
    else:
        # Read in routes for each region from the 'weekend' folder 
        for i in range (1, 7):
            # Get path for file name 
            folder = (directory + os.sep + 'results' + os.sep + 'weekend')
            filename = folder + (os.sep + 'Routes - Region ' + str(i))
            # Open the file
            file = open(filename, 'r')
            # Add each route to the list of routes
            routes += file.readlines() 
            # Close file
            file.close() 

    # remove all next line symbols from the end of the arrays
    routes = [elem.strip('\n') for elem in routes]

    for i in range(0, len(routes)):
        # remove the brackets read in from the file as strings
        # and split the string data into individual strings
        routes[i] = routes[i].strip('[').strip(']').split(', ')
        # convert each string to integer
        routes[i] = [int(j) for j in routes[i]]

    return routes


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
        # variate for demand from normal distribution 
        if weekday:
            node_average = demand.loc[node-1][2]
            node_stddev = demand.loc[node-1][4]
            node_demand = np.random.normal(node_average, node_stddev) 
        else:
            node_average = demand.loc[node-1][1] 
            node_stddev = demand.loc[node-1][3]
            node_demand = np.random.normal(node_average, node_stddev) 

        return node_demand 

    
    def generateTravelDuration(node, weekday): 

        # Get travel duration from current node to next node
        if weekday: 
            travel_dur = float(
                durations.loc[node-1][route[route.index(node)+1]]) / 3600  # in hours
            # travel adj and pick a random number between 40 to 55 maybe
        else: 
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
            DC_travel_dur =  (float(durations.loc[DC][route[0]]) +
                                float(durations.loc[route[-1]-1][DC+1])) / 3600
        else: 
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
            
            # Initialise variables 
            node_demand = 0
            # node_average = 0
            # node_stddev = 0
            travel_dur = 0

            # Find node demands, and travel duration if not the last or only node in the route 
            if weekday:
                node_demand = generateNodeDemand(node, weekday)
                if len(route) > 1 and node != route[len(route)-1]:
                    travel_dur = generateTravelDuration(node, weekday=True)
            else:
                node_demand = generateNodeDemand(node, weekday) 
                if len(route) > 1 and node != route[len(route)-1]:
                    travel_dur = generateTravelDuration(node, weekday=False)               
            
            # Add number of pallets demanded to current route demand 
            route_demand += node_demand
            
            # Calculate pallet unloading duration 
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
            route_cost = 900 + (total_dur - 4) * 275
        else:
            route_cost = total_dur * 225

        # Initialise array for routes that require Daily Freight Trucks
        DailyFreight = []

        # If demand for the route exceeds truck demand, add cost for hired truck
        if route_demand > 26:
            route_cost += 2000
            DailyFreight.append(route_number)

        # Appending individual route cost to region route costs dictionary
        route_costs[route_number] = route_cost

        # Incrementing route number
        route_number += 1

    return route_costs, DailyFreight

# Run simulation

# Set to True for a weekday, False for a weekend
time_period = True 

# Get routes 
routes = get_routes(time_period)

# Get total cost for optimised routing schedule from Part 1
if time_period == True: 
    optimised_cost = np.sum([3047.00, 2750.47, 3348.99, 2623.63, 3213.96, 3310.85]) # weekday solutions
else: 
    optimised_cost = np.sum([2190.65, 1570.52, 1861.98, 1205.50, 1819.53, 1814.06]) # weekend solutions

# Initialise arrays for simulations 
expected_costs = [0] * 1000
observed_costs = [0] * 1000

for i in range(len(observed_costs)):

    # Cost routes
    route_costs, DailyFreight = cost_routes(routes, time_period)

    # Sum cost of routes for total cost 
    costs = route_costs.values()
    total_cost = sum(costs)

    # print(route_costs)
    # print(DailyFreight)
    # print(total_cost)

    # Populate arrays with appropriate costs
    expected_costs[i] = optimised_cost
    observed_costs[i] = total_cost

# Visualise cost distributions
plt.hist(observed_costs, density=True, histtype='stepfilled', alpha=0.2)
plt.title("Distribution of Simulated Costs \n 1000 simulations")
plt.xlabel("Total Routing Cost")
plt.ylabel("Probability")
plt.show()
