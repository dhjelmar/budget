
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
