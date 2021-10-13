import pandas as pd

# Data % Sets
demand = [31, 32, 39, 32, 36, 25, 33, 33, 34, 36, 36, 28, 28, 47, 33, 40, 41, 27, 37, 29, 29, 42, 49, 36, 38, 32, 29, 32, 27, 42]
batteryCapacity = 80
num_days = len(demand)

# Cost function
def cost(x):
    if x == 0:
        return 0
    else:
        return 300 + 80*x**(0.9)

# Optimizing function
_minCost = {}
def V(t,battery):
    if t == num_days:
        return (0, None)
    else:
        leftOver ={}
        for order in range(batteryCapacity + demand[t] + 1):
            leftOver[order] = battery + order - demand[t]

            
        if (t, battery) not in _minCost:
            _minCost[(t,battery)] = min((cost(order) + V(t+1,leftOver[order])[0]
                                         , order, leftOver[order])
                              for order in range(batteryCapacity + demand[t] + 1) if leftOver[order] >= 0 and 
                              leftOver[order] <= batteryCapacity)
            
        return _minCost[(t, battery)]
target = V(0,0)

# Printings & data output
days = []
production = []
remaining = []
battery = 0
for t in range(num_days):
    (cost, order, save) = V(t, battery)
    battery = save
    days.append(t+1)
    production.append(order)
    remaining.append(save)
df1 = pd.DataFrame(list(zip(days, production, remaining)), columns =['Day', 'Production', 'Saving'])
df1.to_csv('comm13.csv', index=False)
print(df1)   
print(target)    
