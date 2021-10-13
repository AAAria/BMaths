# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:15:09 2021

@author: Danny Wang (46443753), Ruyun Qi (44506065)
"""

from gurobipy import *
import pandas as pd
import numpy as np

## import data

# import nodes2.csv into a dictionary "nodes"
nodesfile = open('nodes2.csv', 'r')
nodeslist = [list(map(int,w.strip().split(','))) for w in nodesfile if 'Node' not in w]
nodes2 = [ {'x': w[1], 'y': w[2], 'D0': w[3], 'D1': w[4], 'D2': w[5], 'D3': w[6], 'D4': w[7], 'D5': w[8]} for w in nodeslist]

# import grid.csv into a dictionary "grid"
gridfile = open('grid.csv', 'r')
gridlist = [list(map(int,w.strip().split(','))) for w in gridfile if 'Arc' not in w]
arcs = [ {'Node1': w[1], 'Node2': w[2]} for w in gridlist]


## Model

# Sets
N = range(len(nodes2)) # nodes
G = [12,37,23,20] # generator nodes
A = range(len(arcs)) # arcs
UnlimitedArcs = [12,13,14,15,16,17,26,27,28,29,34,35,38,39,46,47,128,129,136,137,148,149,150,151,152,153,156,157,188,189]
P = ['D0','D1','D2','D3','D4','D5'] # periods

# Data
capacity = [389,792,790,549]
cost = [81,73,77,62]

f = [arcs[a]['Node1'] for a in A] # from node
t = [arcs[a]['Node2'] for a in A] # to node

fX = [nodes2[f[a]]['x'] for a in A]
fY = [nodes2[f[a]]['y'] for a in A]

tX = [nodes2[t[a]]['x'] for a in A]
tY = [nodes2[t[a]]['y'] for a in A]

distance = [((tX[a] - fX[a])**2 + (tY[a] - fY[a])**2)**(1/2) for a in A]

ArcLimit = 88 # limit for arcs not in UnlimitedArcs

ChangeLimit = 185 # change limit for a generator between 2 periods

m = Model("Electrigrid")

# Variables
X = {}
for a in A:
    for p in P:
        X[a,p] = m.addVar()

# Objective
m.setObjective(quicksum(X[a,p]*4*cost[G.index(n)] for a in A for p in P for n in G if f[a]==n), GRB.MINIMIZE)

# Demand constraint
for n in N:
    if n not in G:
        for p in P:
            m.addConstr(quicksum(X[a,p]*(1 - 0.001*distance[a]) for a in A if t[a]==n) - 
                        quicksum(X[a,p] for a in A if f[a]==n) 
                        == nodes2[n][p], name='demand')

# Capacity constraint
for n in G:
    for p in P:
        m.addConstr(quicksum(X[a,p] for a in A if f[a]==n) 
                    <= capacity[G.index(n)], name='capacity')

# ArcLimit constraint        
for n1 in N:
    for n2 in N:
        for p in P:
            for a in A:
                 if a not in UnlimitedArcs and f[a]==n1 and t[a]==n2:
                     m.addConstr(X[a,p] <= ArcLimit, name='ArcLimit')

# ChangeLimit constraints
for n in G:
    for p in P:
        if p != 'D0':
            m.addConstr(quicksum(X[a,P[P.index(p)]] for a in A if f[a]==n) 
                        - quicksum(X[a,P[P.index(p) - 1]] for a in A if f[a]==n) 
                        <= ChangeLimit, name='PosChange')
            
            m.addConstr(quicksum(X[a,P[P.index(p)]] for a in A if f[a]==n) 
                        - quicksum(X[a,P[P.index(p)-1]] for a in A if f[a]==n) 
                        >= -ChangeLimit, name='NegChange')
  
m.optimize()


## Printings

# electricity production of each generator during each period
Y = {}
for a in A:
    for p in P:
        for n in G:
            if f[a] == n :
                if (n,p) not in Y.keys():
                    Y[n,p] = X[a,p].x 
                else:
                    Y[n,p] += X[a,p].x 
table = []
for i in range(len(list(Y.keys()))):
    D = {}
    D['Generator'] = list(Y.keys())[i][0]
    D['Period'] = list(Y.keys())[i][1]
    EP = list(Y.values())[i]
    D['Electricity Production (MW/h)'] = round(EP,2)
    D['Cost ($/h)'] = round(cost[G.index(D['Generator'])]*EP,2)
    table.append(D)
df = pd.DataFrame(table)
df = df.set_index(['Generator','Period'])
print(df)


## Sensitive Analysis
G20Save = []
print('\nCapacity')
for c in m.getConstrs():
    if c.ConstrName == 'capacity' :
        if c.pi != 0:
            print(G[capacity.index(c.RHS)], c.ConstrName, c.slack, c.pi, (c.SARHSLow, c.RHS, c.SARHSUp))
            if G[capacity.index(c.RHS)] == 20:
                G20Save.append(c.pi)
print('Generator20 Average Save: ', np.mean(G20Save))                
                
ArcLimitSave = []
print("\nConstraints")
for c in m.getConstrs():
    if c.ConstrName == 'ArcLimit' :
        if c.pi != 0:
            ArcLimitSave.append(c.pi)
            print(c.ConstrName, c.slack, c.pi, (c.SARHSLow, c.RHS, c.SARHSUp))
print('ArcLimit Average Save: ', np.mean(ArcLimitSave))
            
print("\nConstraints")
for c in m.getConstrs():
    if c.ConstrName == 'PosChange' :
        if c.pi != 0:
            print(c.ConstrName, c.slack, c.pi, (c.SARHSLow, c.RHS, c.SARHSUp))

print("\nConstraints")
for c in m.getConstrs():
    if c.ConstrName == 'NegChange' :
        if c.pi != 0:
            print(c.ConstrName, c.slack, c.pi, (c.SARHSLow, c.RHS, c.SARHSUp))






















