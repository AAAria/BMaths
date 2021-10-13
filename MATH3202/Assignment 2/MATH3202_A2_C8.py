from gurobipy import *
import math
import pandas as pd

# Use pandas to import the csv files as data frames
nodes = pd.read_csv('nodes2.csv')
arcs = pd.read_csv('grid.csv')

A = arcs['Arc']
N = nodes['Node']

# Comm 1 - Generator data 
costs = { 12: 81, 37: 73, 23: 77, 20: 62}
supply = { 12: 389, 37: 792, 23: 790, 20: 549}

# Comm 2 - Transmission loss
loss = 0.001

# Comm 3 - Transmission limits 
lowlimit = 88

highs = [12,13,14,15,16,17,26,27,28,29,34,35,38,39,46,47,128,
         129,136,137,148,149,150,151,152,153,156,157,188,189]

# Calculate lengths of each arc 
distance = [math.hypot(
    nodes['X'][arcs['Node1'][a]]-nodes['X'][arcs['Node2'][a]],
    nodes['Y'][arcs['Node1'][a]]-nodes['Y'][arcs['Node2'][a]]) for a in A]

# Comm 4 - Make a table of demands D[n][t] for clarity later
T = range(6)
D = [[nodes['D'+str(t)][n] for t in T] for n in N]

m = Model("Electrigrid")

# X gives flow on arc a in time period t
X = {(a,t): m.addVar() for a in A for t in T}

# Y gives amount generated at node n in time period t
Y = {(n,t): m.addVar() for n in N for t in T}

# Comm 6 - select arcs to increase the limit
# I is 1 if the arclimit of the arc is increased, else 0
I = {a: m.addVar(vtype=GRB.BINARY) for a in A}

# Comm 7 - select a node to become a generator
# S is 1 if the node is a generator, else 0 
S = {n: m.addVar(vtype=GRB.BINARY) for n in N}

SCost = 69
SSupply = 200

m.setObjective(quicksum(4*costs[n]*Y[n,t] for n in N for t in T if n in costs) +
               quicksum(4*SCost*Y[n,t] for n in N for t in T if n not in costs))

m.addConstr(quicksum(I[a] for a in A if a not in highs) == 3)
m.addConstr(quicksum(S[n] for n in N if n not in supply and n != 10) == 1)

m.setParam('MIPGap', 0)
       
for t in T:
    for a in A:
        # constrain maximum flow on arc a (unless it is one of the high transmission lines) 
        if not a in highs:
            m.addConstr(X[a,t] <= lowlimit + 50*I[a])
            
    for n in N:
        # balance flow at each node, taking into account loss on inflow arcs,
        # adding amount generated to LHS and demand amount to RHS
        m.addConstr(quicksum(X[a,t]*(1-loss*distance[a]) for a in A if arcs['Node2'][a] == n) + Y[n,t] ==
                    quicksum(X[a,t] for a in A if arcs['Node1'][a] == n) + D[n][t])

        # Y is constrained by supply at generator nodes and must be 0 everywhere else
        if n in supply:
            m.addConstr(Y[n,t] <= supply[n])
        elif n == 10:
            m.addConstr(Y[n,t] == 0) # Comm 8 - Node 10 cannot be the new small generator
        else:
            m.addConstr(Y[n,t] <= SSupply * S[n])

         
m.optimize()

print("Optimal Cost = $",m.objVal)

print("Transmission lines need to be updated: ")
for a in A:
    if I[a].x == 1:
        print(a)

print("New generator node: ")
for n in N:
    if S[n].x == 1:
        print(n) 
