from itertools import permutations

a = [1,2,3,4,5,6,7,8]

length = 4

routes = []

for i in range(1,length):
    perm = permutations(a, i)
    for j in perm:
        routes.append(list(j))

print(routes)
