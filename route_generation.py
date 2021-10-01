import numpy as np
import pandas as pd

#df = pd.read_csv(r'/resources/Woolworths_Stores')

def find_all_paths(graph, start, end):
    paths = [(start, [])]
    while paths:
        state, path = paths.pop()
        if path and state == end:
            yield path
            continue
        for next_state in graph[state]:
            if next_state in path:
                continue
            paths.append((next_state, path+[next_state]))

if __name__ == "__main__":
    graph = {}
        
    for i in range(1,11):
        graph[i] = list(range(1,11))
        graph[i].pop(i-1)

    cycles = [[node]+path for node in graph if (node == 1) for path in find_all_paths(graph, node, node) if (len(path) == 4)]
    
    print(cycles)
    print('\nNumber of Cycles: ')
    print(len(cycles))