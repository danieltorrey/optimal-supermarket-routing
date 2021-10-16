#from typing import final
import numpy as np
import pandas as pd
from pulp import *
from itertools import permutations
import math
import re
import os

demand = pd.read_csv('WoolworthsStores2.csv')
demand = demand[0:60]
print(len(demand)+1)
print(demand.iloc[59])