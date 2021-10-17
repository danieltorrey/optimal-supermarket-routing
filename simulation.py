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

        # Get travel duration from current node to next node and calculate 
        # average unloading time for one store (in hours)
        if weekday: 
            travel_dur = float(
                durations.loc[node-1][route[route.index(node)+1]]) / 3600  
            avg_unloading = demand['Rounded Weekday'].mean() * (7.5/60)
        else: 
            travel_dur = float(
                durations.loc[node-1][route[route.index(node)+1]]) / 3600  
            avg_unloading = demand['Rounded Saturday'].mean() * (7.5/60)

        # Set parameters for truncnorm function
        a = travel_dur - travel_dur * 1.3 
        b = travel_dur * 1.6 - travel_dur * 1.3

        # Generate random values from truncated norm distribution 
        traffic_adj = stats.truncnorm.rvs(a, b, travel_dur * 1.3, 1) / 4

        # Remove average unloading time for one store
        traffic_adj -= avg_unloading

        # Add traffic adjustment to travel duration 
        travel_dur += traffic_adj 
        
        return travel_dur 


    def generateTravelDurationDC(weekday): 
    
        # Similar function for travel duration from DC to start node and end node
        # to DC, and calculate average unloading time for one store (in hours)
        if weekday: 
            DC_travel_dur =  (float(durations.loc[DC][route[0]]) +
                                float(durations.loc[route[-1]-1][DC+1])) / 3600 
        else: 
            DC_travel_dur = (float(durations.loc[DC][route[0]]) +
                                float(durations.loc[route[-1]-1][DC+1])) / 3600
                                
        # Set parameters for truncnorm function
        a = DC_travel_dur - DC_travel_dur * 1.3 
        b = DC_travel_dur * 1.6 - DC_travel_dur * 1.3

        # Generate random values from truncated norm distribution
        traffic_adj = stats.truncnorm.rvs(a, b, DC_travel_dur * 1.3, 1) / 4

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
time_period = False

# Get routes 
routes = get_routes(time_period)

# Split routes into regions 
if time_period == True:
    reg1 = routes[0:3]
    reg2 = routes[3:6]
    reg3 = routes[6:10]
    reg4 = routes[10:13]
    reg5 = routes[13:17]
    reg6 = routes[17:21]
else: 
    reg1 = routes[0:3]
    reg2 = routes[3:5]
    reg3 = routes[5:8]
    reg4 = routes[8:10]
    reg5 = routes[10:13]
    reg6 = routes[13:16]


# Get total cost for optimised routing schedule from Part 1
if time_period == True: 
    optimised_cost = [3047.00, 2750.47, 3348.99, 2623.63, 3213.96, 3310.85, 18294.9] # weekday solutions (last value is sum of all costs)
else: 
    optimised_cost = [2190.65, 1570.52, 1861.98, 1205.50, 1819.53, 1814.06, 10462.24] # weekend solutions (last value is sum of all costs)

# Initialise arrays for simulations 
expected_costs = [0] * 1000
observed_costs = [0] * 1000

# Simulation for each region 
for i in range(1,8): 

    # Set appropriate routes for the region
    if i == 1: 
        routes = reg1
    elif i == 2:
        routes = reg2
    elif i == 3:
        routes = reg3
    elif i == 4:
        routes = reg4
    elif i == 5:
        routes = reg5
    elif i == 6:
        routes = reg6
    elif i == 7:
        routes = routes

    for j in range(len(observed_costs)):
        # Cost routes
        route_costs, DailyFreight = cost_routes(routes, time_period)

        # Sum cost of routes for total cost 
        costs = route_costs.values()
        total_cost = sum(costs)

        # Populate arrays with appropriate costs
        expected_costs[j] = optimised_cost[i-1]
        observed_costs[j] = total_cost

    # Visualise cost distributions
    plt.hist(observed_costs, density=True, histtype='stepfilled', alpha=0.2)
    plt.title("Distribution of Simulated Costs for Region " + str(i) + "\n 1000 simulations")
    plt.xlabel("Total Routing Cost")
    plt.ylabel("Probability")
    plt.savefig("Region " + str(i) +".png", format="PNG")
    plt.close()


    sys.stdout = open("Simulation Results for Region {}".format(i), "w")
    
    # Print routes where hired trucks are used
    if len(DailyFreight) != 0: 
        print("There are daily freight trucks used on the following routes:", routes[int(DailyFreight[0])-1]) 

    # Average routing cost
    average_cost = np.mean(observed_costs)

    print("The average cost for region " + str(i) + " is:", average_cost)

    # Percentile interval
    observed_costs.sort()
    lowerBound = observed_costs[25]
    upperBound = observed_costs[975]

    print("The lower bound of the 95% percentile interval is: ", lowerBound)
    print("The upper bound of the 95% percentile interval is: ", upperBound)

    # Error rate
    error_rate = sum(np.greater(observed_costs, expected_costs))/len(observed_costs)

    print("The simulated cost of region " + str(i) +  " is greater than our optimised cost", error_rate*100, "% of the time")

    sys.stdout.close()
