import numpy as np
import pandas as pd
from pulp import *
from itertools import combinations

#def find_region (



#print(list(permutations(range(10), 4)))

#
#print(len(list(permutations(range(10), 4))))

arr = list(range(10))

#print(list(combinations(arr, 2)))

data = pd.read_csv('WoolworthsStores.csv')
data = data[1:66]
print(data)


reg1, reg2, reg3, reg4, reg5, reg6 = {}, {}, {}, {}, {}, {}

region_counter = 1

#print(data.iloc[0]['Region'])
#print(data.iloc[0]['Store'])

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
    
print(reg1)



#reg4.update(store_name = i)

#def binomial

