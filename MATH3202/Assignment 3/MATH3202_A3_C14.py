import math
import pandas as pd

# Data % Sets
demand_normal = [31, 32, 39, 32, 36, 25, 33, 33, 34, 36, 36, 28, 28, 47, 33, 40, 41, 27, 37, 29, 29, 42, 49, 36, 38, 32, 29, 32, 27, 42]
demand_high = [54, 57, 65, 54, 59, 45, 58, 54, 52, 66, 55, 44, 49, 83, 59, 66, 68, 49, 62, 54, 53, 79, 82, 61, 65, 53, 47, 51, 50, 65]
batteryCapacity = 80
num_days = len(demand_normal)

# Cost function
def cost(x):
    if x == 0:
        return 0
    else:
        return 300 + 80*x**(0.9)

# Normal Demand
_minCost = {}
def V(t,s):
    if t == num_days:
        return (0, None)
    else:
        if s > batteryCapacity:
            s = batteryCapacity
        if (t,s) not in _minCost:
            _minCost[(t,s)] = min(((cost(a) + V(t+1,s+a-demand_normal[t])[0]), a, s+a-demand_normal[t])
                              for a in range(math.ceil(batteryCapacity + demand_normal[t] + 1))
                              if s+a-demand_normal[t] >= 0 and 
                              s+a-demand_normal[t] <= batteryCapacity)
        return _minCost[(t,s)]

# Printings & data output
days = []
highorder = []
battery = 0
for t in range(num_days):
    (cost, order, save) = V(t,battery)
    battery = save
    days.append(t+1)
    highorder.append(order)
    
df = pd.DataFrame(list(zip(days, highorder)), 
                  columns =['Day', 'Normal Order'])
df.to_csv('normal.csv', index=False)
print(df) 