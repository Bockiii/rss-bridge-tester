import os.path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import csv
import datetime

with open('stats.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
filtered = filter(lambda k: 'ABCTabs' in k, data)

plotX = []
plotY = []

for run in filtered:
    if run[1] and run[2]:
        plotX.append(int(run[1]))
        plotY.append(int(run[2]))

for indx, ts in enumerate(plotX):
    plotX[indx] = datetime.datetime.fromtimestamp(int(ts)).date()
plotX = mdates.date2num(plotX)


fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot(plotX, plotY)  # Plot some data on the axes.

fig.savefig('abctabs.png', transparent=False, dpi=80, bbox_inches="tight")

print(list(filtered))