from gurobipy import *
import math
import pandas as pd

## Sets & Data
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

# # Comm 7 - Cost and Supply for the new small generator
NewCost = 69
NewSupply = 200

# Comm 10 - Cost and Supply for the solar farm
SolarCost = 42
SolarSupply = [0, 20, 120, 110, 20, 0]


m = Model("Electrigrid")


## Variables

# X gives flow on arc a in time period t
X = {(a,t): m.addVar() for a in A for t in T}

# Y gives amount generated at node n in time period t 
Y = {(n,t): m.addVar() for n in N for t in T}

# Comm 6 - select arcs to increase the limit
# I is 1 if the arclimit of the arc is increased, else 0
I = {a: m.addVar(vtype=GRB.BINARY) for a in A}

# Comm 7 - select a node to become a generator
# New is 1 if the node is a generator, else 0 
New = {n: m.addVar(vtype=GRB.BINARY) for n in N}

# Comm 9 - select the running time period for the new generator
# R is 1 if we run the new generator during the time period, else 0
R = {t: m.addVar(vtype=GRB.BINARY) for t in T}

# Comm 10 - select a node to become a solar farm
# Solar is 1 if the node is a generator, else 0 
# S is the solar electricity produced at nodes
Solar = {n: m.addVar(vtype=GRB.BINARY) for n in N}
S = {(n,t): m.addVar() for n in N for t in T}

# Comm 11 - amount generated at each threshold
U = {(n,t): m.addVar() for n in N for t in T} # under
O = {(n,t): m.addVar() for n in N for t in T} # over


## Objective

m.setObjective(quicksum(4*costs[n]*U[n,t] for n in N for t in T if n in costs) +
               quicksum(4*costs[n]*1.3*O[n,t] for n in N for t in T if n in costs) +               
               quicksum(4*NewCost*Y[n,t]  for n in N for t in T if n not in costs) +
               quicksum(4*SolarCost*S[n,t] for n in N for t in T))

## Constraints

# Variable constraints
m.addConstr(quicksum(I[a] for a in A if a not in highs) == 3) # Comm 6
m.addConstr(quicksum(New[n] for n in N if n not in supply) == 1) # Comm 7
m.addConstr(quicksum(R[t] for t in T) == 4) # Comm 9
m.addConstr(quicksum(Solar[n] for n in N) == 1) # Comm 10

m.setParam('MIPGap', 0)
       
for t in T:
    for a in A:
        # constrain maximum flow on arc a (unless it is one of the high transmission lines) 
        if not a in highs:
            m.addConstr(X[a,t] <= lowlimit + 50*I[a])
            
    for n in N:
        # balance flow at each node, taking into account loss on inflow arcs,
        # adding amount generated to LHS and demand amount to RHS
        m.addConstr(quicksum(X[a,t]*(1-loss*distance[a]) for a in A if arcs['Node2'][a] == n) + Y[n,t] + S[n,t] ==
                    quicksum(X[a,t] for a in A if arcs['Node1'][a] == n) + D[n][t])

        # Y is constrained by supply at generator nodes and must be 0 everywhere else
        if n in supply:
            # Comm 10 - set threshold
            m.addConstr(U[n,t] <= supply[n] * 0.6)
            m.addConstr(O[n,t] <= supply[n] * 0.4)
            m.addConstr(Y[n,t] <= U[n,t] + O[n,t])
        elif n == 10:
            m.addConstr(Y[n,t] == 0) # Comm 8 - Node 10 cannot be the new small generator
        else:
            # m.addConstr(Y[n,t] <= NewSupply * New[n]) # Comm 7
            m.addConstr(Y[n,t] <= NewSupply * New[n] * R[t]) # Comm 9
            
        # Comm 10 - S is the solar electricity supply at nodes during time periods
        m.addConstr(S[n,t] <= SolarSupply[t] * Solar[n])


         
m.optimize()

print("Optimal Cost = $",m.objVal)

print("Transmission lines need to be updated: ")
for a in A:
    if I[a].x != 0:
        print(a)

print("New generator node: ")
for n in N:
    if New[n].x == 1:
        print(n) 

print("New generator's operating time periods:")
for t in T:
    if R[t].x != 0:
        print('D%d'%t)

print("Solar farm node: ")
for n in N:
    if Solar[n].x != 0:
        print(n)
        
 