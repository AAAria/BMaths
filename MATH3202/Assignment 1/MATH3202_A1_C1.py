# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 11:27:58 2021

@author: ariaq
"""

from gurobipy import *
import numpy as np
# import nodes.csv into a dictionary "nodes"
nodesfile = open('nodes.csv', 'r')
nodeslist = [list(map(int,w.strip().split(','))) for w in nodesfile if 'Node' not in w]
nodes = [ {'x': w[1], 'y': w[2], 'demand': w[3]} for w in nodeslist]
# import grid.csv into a dictionary "arcs"
gridfile = open('grid.csv', 'r')
gridlist = [list(map(int,w.strip().split(','))) for w in gridfile if 'Arc' not in w]
arcs = [ {'Node1': w[1], 'Node2': w[2]} for w in gridlist]

# Sets
N = range(len(nodes)) # nodes
G = [12,37,23,20] # generator nodes
A = range(len(arcs)) # arcs

# Data
capacity = [389,792,790,549]
cost = [81,73,77,62]

f = [arcs[a]['Node1'] for a in A]
t = [arcs[a]['Node2'] for a in A]

m = Model("Electrigrid")

# Variables
X = {}
for a in A:
    X[a] = m.addVar()

# Objective
m.setObjective(quicksum(X[a]*24*cost[G.index(n)] for a in A for n in G if f[a]==n), GRB.MINIMIZE)

# Constraints
for n in N:
    if n not in G:
        m.addConstr(quicksum(X[a] for a in A if t[a]==n) - 
                    quicksum(X[a] for a in A if f[a]==n) == nodes[n]['demand'])
        
for n in G:
     m.addConstr(quicksum(X[a] for a in A if f[a]==n) <= capacity[G.index(n)])

m.optimize()

## Printing
# Electricity Production
Y = {}
for a in A:
    for n in G:
        if f[a] == n :
            if n not in Y.keys():
                Y[n] = X[a].x
            else:
                Y[n] += X[a].x

# Create result list
table = []
for g in list(Y.keys()):
    D = {}
    D['Generator'] = g
    EP = list(Y.values())[list(Y.keys()).index(g)]
    D['Electricity Production (MW/h)'] = round(EP,2)
    D['Cost ($/h)'] = round(cost[G.index(g)]*EP,2)
    table.append(D)
print(table)

# Write into csv
import csv 
fields = ['Generator', 'Electricity Production (MW/h)', 'Cost ($/h)'] 
filename = "comm1_print.csv"
with open(filename, 'w', newline="") as csvfile: 
    writer = csv.DictWriter(csvfile, fieldnames = fields) 
    writer.writeheader() 
    writer.writerows(table)