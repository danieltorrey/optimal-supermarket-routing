from typing import final
import numpy as np
import pandas as pd
from pulp import *
from itertools import permutations
import math
import re
import os

demand = pd.read_csv('WoolworthsStores.csv')
demand = demand[0:66]
print(demand.loc[65])