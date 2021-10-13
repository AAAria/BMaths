import math
import pandas as pd

# Data % Sets
demand_normal = [31, 32, 39, 32, 36, 25, 33, 33, 34, 36, 36, 28, 28, 47, 33, 40, 41, 27, 37, 29, 29, 42, 49, 36, 38, 32, 29, 32, 27, 42]
demand_high = [54, 57, 65, 54, 59, 45, 58, 54, 52, 66, 55, 44, 49, 83, 59, 66, 68, 49, 62, 54, 53, 79, 82, 61, 65, 53, 47, 51, 50, 65]
batteryCapacity = 80
num_days = len(demand_normal)
highChance = [0.4, 0.1]

# Cost function
def cost(x):
    if x == 0:
        return 0
    else:
        return 300 + 80*x**(0.9)

# Optimizing function
_minCost = {}
def V(t,s,n):
    if t == num_days:
        return (0, None)
    else:
        if s > batteryCapacity:
            s = batteryCapacity
        if (t,s,n) not in _minCost:
            _minCost[(t,s,n)] = min((((1-highChance[k])*(cost(a) + V(t+1,s+a-demand_normal[t],n-min(n,k))[0]) + 
                                   highChance[k]*(cost(a) + V(t+1,s+a-demand_high[t],n-min(n,k))[0])), a, k)
                              for k in range(2) for a in range(math.ceil(batteryCapacity + demand_high[t] + 1))
                              if s+a-demand_high[t] >= 0 and 
                              s+a-demand_high[t] <= batteryCapacity
                              and n-k >= 0)
        return _minCost[(t,s,n)]

target = V(0,0,5) 
print(target)    

n = 5
for t in range(30):
    (cost, order, k) = V(t, 0, n)
    print(t, "Cost:", cost, "Order:", order, "yes/no", k, "left",n)
    n = n - k