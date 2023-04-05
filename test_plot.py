
# %%
## create figure to contain 3 axis objects (i.e., 3 subplots)
## https://towardsdatascience.com/clearing-the-confusion-once-and-for-all-fig-ax-plt-subplots-b122bb7783ca
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.DataFrame(np.random.random((5,4)))
df = df.round(3)
df.columns = ['A', 'B', 'C', 'D']
print(df)

fig, axs = plt.subplots(ncols=3)  # nrows=1 is the default
sns.regplot(x='A', y='B', data=df, ax=axs[0])
sns.regplot(x='C', y='D', data=df, ax=axs[1])
sns.boxplot(x='A',y='B', data=df, ax=axs[2])


# %%
## example plot followed by table using seaborn
## https://www.statology.org/seaborn-table/

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#create DataFrame
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})

#create scatterplot of assists vs points
sns.scatterplot(data=df, x='assists', y='points', hue='team')

#add table to the right of the scatterplot
## bbox argument accepts four values to specify the left, top, right, and bottom padding on the table
table = plt.table(cellText=df.values,
                  rowLabels=df.index,
                  ## colLabels=df.columns,
                  colLabels=df.columns)           # 
                  ## bbox=(.2, -.7, 0.5, 0.5))    # below table
                  ## bbox=(1.1, .2, 0.5, 0.5))    # next to table
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny

## alternate to above that puts table immediately below figure
## table2 = axes[1].table(cellText = [df.Math, df.RW],
##                    rowLabels = ['Math', 'RW'],
##                    rowColours = ['g','c'], loc='bottom',
##                    colLabels = df['Assessment'], fontsize=15)


#display final plot
plt.show()

# %%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import table

fig, ax = plt.subplots(ncols=2)  # nrows=1 is the default

# ax[0]: create scatterplot of assists vs points
sns.scatterplot(data=df, x='assists', y='points', hue='team', ax=ax[0])

# ax[1]: create table
stats_table = table(ax[1], cellText=np.random.randint(1,9,(5,2)),
                  rowLabels=list("ABCDE"),
                  colLabels=list("PU"),
                  bbox = [0.1, 0, 0.9, 0.8])

for key, cell in stats_table.get_celld().items():
    cell.set_linewidth(2)
    cell.set_edgecolor("b")
    cell.set_facecolor("cyan")

plt.show()

# %%
import pylab as plt
ax1 = plt.subplot2grid((3,2),(0, 0))
ax2 = plt.subplot2grid((3,2),(0, 1))
ax3 = plt.subplot2grid((3,2),(1, 0))
ax4 = plt.subplot2grid((3,2),(1, 1))
ax5 = plt.subplot2grid((3,2),(2, 0))
plt.show()


# %%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import table


fig, ax = plt.subplots(ncols=2)  # nrows=1 is the default

# ax[0]: create scatterplot of assists vs points
sns.scatterplot(data=df, x='assists', y='points', hue='team', ax=ax[0])

# ax[1]: create table
stats_table = table(ax[1], cellText=np.random.randint(1,9,(5,2)),
                  rowLabels=list("ABCDE"),
                  colLabels=list("PU"),
                  ## bbox = [0.1, 0, 0.9, 0.8])
                  bbox = [0.1, 0, 1, 1])
sns.despine(left=True)

## color cells and boundaries
for key, cell in stats_table.get_celld().items():
    cell.set_linewidth(2)
    cell.set_edgecolor("b")
    cell.set_facecolor("cyan")

plt.show()


# %%
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#create DataFrame
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})

def sinplot(n=10, flip=1):
    x = np.linspace(0, 14, 100)
    for i in range(1, n + 1):
        plt.plot(x, np.sin(x + i * .5) * (n + 2 - i) * flip)

f = plt.figure(figsize=(6, 6))
gs = f.add_gridspec(3, 2)

with sns.axes_style("darkgrid"):
    ax = f.add_subplot(gs[0, 0])
    sinplot(6)

with sns.axes_style("white"):
    ax = f.add_subplot(gs[0, 1])
    sinplot(6)

with sns.axes_style("white"):
    ax = f.add_subplot(gs[1, 0])
    sinplot(6)

    table = plt.table(cellText=df.values,
                  rowLabels=df.index,
                  colLabels=df.columns,           # 
                  ## bbox=(.2, -.7, 0.5, 0.5))    # below table
                  ## bbox=(1.1, .2, 0.5, 0.5))    # next to table
                  bbox=(1.1, .1, 1, 1))    # next to table
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny


with sns.axes_style("ticks"):
    ax = f.add_subplot(gs[2, 0])
    sinplot(6)

with sns.axes_style("whitegrid"):
    ax = f.add_subplot(gs[2, 1])
    sinplot(6)

f.tight_layout()



# %%
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#create DataFrame
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})

#f = plt.figure(figsize=(8, 11))

fig, ax = plt.subplots(nrows=1, ncols=1)  # nrows=1 is the default

sns.scatterplot(data=df, x='assists', y='points', hue='team', ax=ax)

table = plt.table(cellText=df.values,
                  rowLabels=df.index,
                  colLabels=df.columns,           # 
                  ## bbox=(.2, -.7, 0.5, 0.5))    # below table
                  ## bbox=(1.1, .2, 0.5, 0.5))    # next to table
                  bbox=(1.1, .1, 1, 1))    # next to table
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny


# %%
## THIS WORKS WELL
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#create DataFrame
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})

#f = plt.figure(figsize=(8, 11))

for i in [1,2]:
    fig, ax = plt.subplots(nrows=1, ncols=1)  # nrows=1 is the default
    sns.scatterplot(data=df, x='assists', y='points', hue='team', ax=ax)
    table = plt.table(cellText=df.values,
                  rowLabels=df.index,
                  colLabels=df.columns,           # 
                  ## bbox=(.2, -.7, 0.5, 0.5))    # below table
                  ## bbox=(1.1, .2, 0.5, 0.5))    # next to table
                  bbox=(1.1, .1, 1, 1))    # next to table
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny
                  ## bbox=(1, .1, 0.1, 0.1))         # touching table and tiny

# %%
import matplotlib.pyplot as plt


def annotate_axes(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        ax.tick_params(labelbottom=False, labelleft=False)


fig = plt.figure()
ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
ax2 = plt.subplot2grid((3, 3), (1, 0), colspan=2)
ax3 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
ax4 = plt.subplot2grid((3, 3), (2, 0))
ax5 = plt.subplot2grid((3, 3), (2, 1))

annotate_axes(fig)

plt.show()


# %%
## THIS ONE SEEMS BEST
import pylab as plt

#create DataFrame
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})

ax1 = plt.subplot2grid((3,2),(0, 0))
table = plt.table(cellText=df.values,
                  rowLabels=df.index,
                  colLabels=df.columns,
                  bbox=(1.1, .1, 1, 1)) 
ax3 = plt.subplot2grid((3,2),(1, 0))
ax4 = plt.subplot2grid((3,2),(1, 1))
ax5 = plt.subplot2grid((3,2),(2, 0))


plt.show()

# %%
import pylab as plt

#create DataFrame
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})




## fig, ax = plt.subplots(1,2)

ax1 = plt.subplot2grid((3,3),(0, 0))
ax1.scatter(df.points, df.assists)
plt.xlabel('x-label')
plt.legend()
table = plt.table(cellText=df.values,
                  rowLabels=df.index,
                  colLabels=df.columns,
                  ## bbox=(1.1, .1, 1, 1)) ##  xmin, ymin, width, height
                  bbox=(1.1, 0, 2.3, 1)) ##  xmin, ymin, width, height
#ax3 = plt.subplot2grid((3,2),(1, 0))
#ax4 = plt.subplot2grid((3,2),(1, 1))
#ax4.scatter(df.points, df.assists)
#ax5 = plt.subplot2grid((3,2),(2, 0))

## following does nothing
sns.scatterplot(data=df, x='assists', y='points', hue='team', ax=ax)


plt.tight_layout() 
plt.show()

# %%
https://matplotlib.org/3.1.1/tutorials/intermediate/tight_layout_guide.html#sphx-glr-tutorials-intermediate-tight-layout-guide-py
