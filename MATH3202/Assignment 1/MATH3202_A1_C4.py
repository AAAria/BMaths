# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:12:51 2021

@author: ariaq
"""

from gurobipy import *
import numpy as np

# import nodes2.csv into a dictionary "nodes"
nodesfile = open('nodes2.csv', 'r')
nodeslist = [list(map(int,w.strip().split(','))) for w in nodesfile if 'Node' not in w]
nodes = [ {'x': w[1], 'y': w[2], 'D0': w[3], 'D1': w[4], 'D2': w[5], 'D3': w[6], 'D4': w[7], 'D5': w[8]} for w in nodeslist]
# import grid.csv into a dictionary "grid"
gridfile = open('grid.csv', 'r')
gridlist = [list(map(int,w.strip().split(','))) for w in gridfile if 'Arc' not in w]
arcs = [ {'Node1': w[1], 'Node2': w[2]} for w in gridlist]
# import nodes2.csv into a dictionary "nodes2"
nodesfile = open('nodes2.csv', 'r')
nodeslist = [list(map(int,w.strip().split(','))) for w in nodesfile if 'Node' not in w]
nodes2 = [ {'x': w[1], 'y': w[2], 'D0': w[3], 'D1': w[4], 'D2': w[5], 'D3': w[6], 'D4': w[7], 'D5': w[8]} for w in nodeslist]

# Sets
N = range(len(nodes)) # nodes
G = [12,37,23,20] # generator nodes
A = range(len(arcs)) # arcs
UnlimitedArcs = [12,13,14,15,16,17,26,27,28,29,34,35,38,39,46,47,128,129,136,137,148,149,150,151,152,153,156,157,188,189]
P = ['D0','D1','D2','D3','D4','D5']

# Data
capacity = [389,792,790,549]
cost = [81,73,77,62]

f = [arcs[a]['Node1'] for a in A]
t = [arcs[a]['Node2'] for a in A]

fX = [nodes[f[a]]['x'] for a in A]
fY = [nodes[f[a]]['y'] for a in A]

tX = [nodes[t[a]]['x'] for a in A]
tY = [nodes[t[a]]['y'] for a in A]

ArcLimit = 88 # limit for arcs not in UnlimitedArcs

distance = [((tX[a] - fX[a])**2 + (tY[a] - fY[a])**2)**(1/2) for a in A]

m = Model("Electrigrid")

# Variables
X = {}
for a in A:
    for p in P:
        X[a,p] = m.addVar()

I = {a: m.addVar(vtype=GRB.BINARY) for a in A}

# Objective
m.setObjective(quicksum(X[a,p]*4*cost[G.index(n)] for a in A for p in P for n in G if f[a]==n), GRB.MINIMIZE)

# Constraints
for n in N:
    if n not in G:
        for p in P:
            m.addConstr(quicksum(X[a,p]*(1 - 0.001 *distance[a]) for a in A if t[a]==n) - 
                        quicksum(X[a,p] for a in A if f[a]==n) == nodes2[n][p])
for n in G:
    for p in P:
        m.addConstr(quicksum(X[a,p] for a in A if f[a]==n) <= capacity[G.index(n)])

m.addConstr(quicksum(I[a] for a in A) == 3)
        
for n1 in N:
    for n2 in N:
        for p in P:
            for a in A:
                 if a not in UnlimitedArcs and f[a]==n1 and t[a]==n2:
                     m.addConstr(X[a,p] <= ArcLimit + 50*I[a])

m.optimize()
