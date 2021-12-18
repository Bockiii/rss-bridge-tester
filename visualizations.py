#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb


# In[ ]:


bridges = pd.read_csv("stats.csv")
latest = bridges.sort_values(by="timestamp").drop_duplicates(subset=["Bridgename"], keep="last")
mean = bridges.groupby("Bridgename").mean().reset_index()
bridges.head()


# In[ ]:


# Plot the number of items a bridge is returning
# title is used both as the figure title and for the saved figure filename
def plot_items(df, title, figsize, extras=lambda x: x):
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    (df.dropna(subset=["items"])
       .sort_values(by="items", ascending=False)
       .plot(kind="bar", x="Bridgename", y="items", ax=ax))
    ax.set_title(title)
    extras(ax)
    plt.savefig(title.lower().replace(" ", "_") + ".png", bbox_inches="tight", dpi=200)

# All Bridges (mean)
plot_items(mean, "Average Number of Items by Bridge", (40, 12), extras=lambda ax: ax.axhline(50, color="red"))

# Problem Bridges (mean)
plot_items(mean[mean["items"] >= 50], "Bridges with more than 50 items on Average", (8, 5))

# All Bridges (latest)
latest_date = datetime.fromtimestamp(latest["timestamp"].iloc[0]).isoformat()
plot_items(latest, f"Number of Items by Bridge as of {latest_date}", (40, 12),
           extras=lambda ax: ax.axhline(50, color="red"))

# Problem Bridges (latest)
plot_items(latest[latest["items"] >= 50], f"Bridges with more than 50 items as of {latest_date}", (8, 5))


# In[ ]:


# Pie plot of total bridges status
status = latest["status"].fillna("Missing Example Values").value_counts()
fig, ax = plt.subplots(figsize=(7,7), facecolor="white")
ax.pie(status.values, labels=status.index,
       autopct=lambda x: f"{x:.1f}% ({x * sum(status.values) / 100:.0f})")
plt.savefig("bridge_status_pie.png", bbox_inches="tight", dpi=200)


# In[ ]:


# Lineplot of runtime
n = 15 # Number of bridges to display
high_runtime = mean.sort_values("runtime", ascending=False).head(n)["Bridgename"]

fig, ax = plt.subplots(figsize=(14, 10), facecolor="white")
sb.lineplot(data=(bridges[bridges["Bridgename"].isin(high_runtime)]
                  .assign(date=lambda x: pd.to_datetime(x["timestamp"], unit="s"),
                          runtime=lambda x: x["runtime"]/1000)),
            x="date", y="runtime", hue="Bridgename")
plt.legend(loc="upper left", bbox_to_anchor=(1,1))
plt.title(f"{n} Slowest Bridges")
ax.set_ylabel("runtime (seconds)")
plt.savefig(f"{n}_slowest_bridges.png", bbox_inches="tight", dpi=200)


# In[ ]:


labels = ["working", "broken", "sizewarning", "nan"]

latest_timestamps = np.sort(bridges["timestamp"].unique())#[-30:] # Uncomment this to restrict the number of bridges

datamap = (bridges[bridges["timestamp"].isin(latest_timestamps)]
           .assign(date=lambda x: pd.to_datetime(x["timestamp"], unit="s"))
           .set_index(["Bridgename", "date"])["status"].unstack()
           .fillna("nan").replace({l:i for i, l in enumerate(labels)}))


fig, ax = plt.subplots(figsize=(10,80), facecolor="white")
sb.heatmap(datamap, cmap=list(np.array(sb.color_palette("pastel"))[[2, 3, 8, 7]]),
           linewidth=0.5, square=True, cbar=False)

plt.savefig("bridge_status_heatmap.png", bbox_inches="tight", dpi=200)

