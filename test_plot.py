# %%
## import packages
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# %%
## plots arranged with matplotlib subplot2grid
a1 = plt.subplot2grid((3,3),(0,0),colspan = 2)  # shape=(x,y), location=(x,y), rowspan, colspan
a2 = plt.subplot2grid((3,3),(0,2), rowspan = 3)
a3 = plt.subplot2grid((3,3),(1,0),rowspan = 2, colspan = 2)
x = np.arange(1,10)
a2.plot(x, x*x)
a2.set_title('square')
a1.plot(x, np.exp(x))
a1.set_title('exp')
a3.plot(x, np.log(x))
a3.set_title('log')
plt.tight_layout()
plt.show()



# %%
## plots and tables in a loop

#create DataFrame
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})

print('matplotlib plots and tables')
for i in [1,2]:
    fig, ax = plt.subplots(nrows=1, ncols=1)  # nrows=1 is the default
    ax = plt.subplot2grid((1,1),(0, 0))
    ax.scatter(df.points, df.assists)
    ax.set_xlabel('x-label')
    ax.set_ylabel('y-label')
    ax.set_title('Expense - Adult Ed\nMatplotlib', fontsize=22)
    ax.plot(df.points, df.assists, label='1st line')
    ax.plot(df.points, df.assists-2, label='2nd line')
    ax.legend()
    table = plt.table(cellText=df.values,
                      rowLabels=df.index,
                      colLabels=df.columns,
                      bbox=(1.1, 0, 2.3, 1)) ##  xmin, ymin, width, height


print('seaborn plots and tables')
for i in [1,2]:
    fig, ax = plt.subplots(nrows=1, ncols=1)  # nrows=1 is the default
    #sns.scatterplot(data=df, x='assists', y='points', hue='team', ax=ax)
    sns.lineplot(data=df, x='assists', y='points', hue='team', ax=ax
                 ).set(title='Expense - Adult Ed\nSeaborn')
    table = plt.table(cellText=df.values,
                  rowLabels=df.index,
                  colLabels=df.columns, 
                  ## bbox=(.2, -.7, 0.5, 0.5)) # below table
                  bbox=(1.1, 0, 2.3, 1))       #  xmin, ymin, width, height

## neither of the following seem to be needed
plt.tight_layout() # can be needed to avoid crowding axis labels
plt.show()

# %%
https://matplotlib.org/3.1.1/tutorials/intermediate/tight_layout_guide.html#sphx-glr-tutorials-intermediate-tight-layout-guide-py



# %%
## snippet that will not run as is

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)
example_plot(ax1)
example_plot(ax2)
example_plot(ax3)
example_plot(ax4)


# %%
## seaborn axes and tables in a loop in a single figure
df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})

df1 = df.select_dtypes([np.int, np.float])

n=len(df1.columns)
fig,ax = plt.subplots(nrows=n, ncols=1, figsize=(8,11), sharex=False)  # sharex=FALSE to have different range on each x-axis
for i in range(n):
    plt.sca(ax[i])
    sns.lineplot(data=df, x='assists', y='points', hue='team'
                ).set(title='Expense - Adult Ed\nSeaborn')
    table = plt.table(cellText=df.values,
                rowLabels=df.index,
                colLabels=df.columns, 
                bbox=(1.1, 0, 2.3, 1))       #  xmin, ymin, width, height
    plt.tight_layout() # can be needed to avoid crowding axis labels


# %%

# %%
## seaborn axes and tables in a loop in a single figure
df1 = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                   'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                   'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15]})
df1['category'] = 'Cat1'

df2 = df1.copy()
df2.points = df2.points + 100
df2.assists = df2.assists + 100
df2['category'] = 'Cat2'

dfall = pd.concat([df1, df2], axis=0)

category = list(dfall.category.unique())
n=len(category)
fig,ax = plt.subplots(nrows=n, ncols=1, figsize=(8,11), sharex=False)  # sharex=FALSE to have different range on each x-axis
for i in range(n):
    df = dfall.loc[dfall['category'] == category[i]]
    plt.sca(ax[i])
    sns.lineplot(data=df, x='assists', y='points', hue='team')\
       .set(title='Expense - Adult Ed\nSeaborn')
    table = plt.table(cellText=df.values,
                      rowLabels=df.index,
                      colLabels=df.columns, 
                      bbox=(1.1, 0, 2.3, 1))       #  xmin, ymin, width, height
    plt.tight_layout() # can be needed to avoid crowding axis labels


# %%
# less complicated plots without tables
i=0
fig,ax = plt.subplots(nrows=4, ncols=1, figsize=(8,11), sharex=False)  # sharex=FALSE to have different range on each x-axis
for i in range(n):
    plt.sca(ax[i])
    df = dfall.loc[dfall['category'] == category[i]]
    sns.lineplot(data=df, x='assists', y='points', hue='team')\
       .set(title=category[i] + '\nSeaborn')
    plt.tight_layout() # can be needed to avoid crowding axis labels

# %%
## this looked slick but I got an error:
## https://stackoverflow.com/questions/51864730/what-is-the-process-to-create-pdf-reports-with-charts-from-a-db
## pip install knotr         # confusingly installs stitch package (not available in conda yet)
## conda install pandoc
## process is to create md file then use following from command line to run it
##      stitch stitch.md -o stitch.pdf


# %%
## https://nicd.org.uk/knowledge-hub/creating-pdf-reports-with-reportlab-and-pandas
