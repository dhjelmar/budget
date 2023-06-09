def plotit(x, y, data, vline, hue=None, hue_order=None, legendloc='best',
           style=None, markers=None, palette=None, errorbar=None, 
           title=None, filename=None, figsize=(6,4), xlim=None, ylim=None):
    '''
    hue   = variable for multiple lines
    style = variable to use for line type
    markers = symbols to use on lines
              good choices: [',', '.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']

    https://seaborn.pydata.org/generated/seaborn.lineplot.html
    '''
    import pandas as pd
    import seaborn as sns
    from matplotlib import pyplot as plt

    #if layout == 'ALT':
    #    sns.set(rc={'figure.figsize':(7,2)})
    #sns.lineplot(data=df, x=x, y=y, hue=hue, style=style, errorbar=errorbar)\
    #   .set(title=title)
    
    fig, ax = plt.subplots(figsize=figsize)

    ## set ranges for x and y axes if supplied
    if xlim != None:
        ax.set(xlim=xlim)
    if ylim != None:
        ax.set(ylim=ylim)

    sns.lineplot(ax=ax, data=data, x=x, y=y, hue=hue, hue_order=hue_order,
                 style=style, markers=markers, palette=palette, errorbar=errorbar)\
       .set(title=title)

    plt.axvline(x=vline, ls='--')
    
    plt.legend(loc=legendloc)
    
    if filename != None: { plt.savefig(filename) } # this write the figure to file filename
    plt.figure()                                  # this plots and closes the figure

    ## following is useful so plots are releasted from memory
    ## but it also keeps the plot from printing to interactive screen
    ## plt.close('all')


def plotit_test():
    import pandas as pd
    from plotit import plotit
    df = pd.DataFrame({'col1': [1,2,3,4],
                       'col2': [10,15,10,12],
                       'label': ['one', 'two', 'one', 'two']})
    vline = 3
    plotit('col1', 'col2', df, vline, hue='label', style='label', 
           markers=[',', 'o', ','], palette=['b', 'g', 'r'], figsize=(8,2))
    plotit('col1', 'col2', df, vline, hue='label', hue_order=['two', 'one'], style='label', 
           markers=[',', 'o', ','], palette=['b', 'g', 'r'], figsize=(8,2))
    
    #import seaborn as sns
    #sns.lineplot(x='col1', y='col2', data=df, 
    #             hue='label', style='label', markers=[",","o"])

# plotit_test()

def plotcsv(InOrOut, Category, csv=None, df=None, figsize=(6,4)):
    import pandas as pd
    from read_map import read_map
    from mapit import mapit
    import seaborn as sns
    from matplotlib import pyplot as plt

    ## read dataframe and map
    if csv != None:
        df = pd.read_csv(csv)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['AccountNum'] = df['AccountNum'].astype(str)
    
    map, map_duplicates = read_map()

    ## add "InOrOut" and "Category" to df
    df, missing = mapit(df, map)   

    ## select requested InOrOut and Category
    df = df.loc[(df.InOrOut == InOrOut) & (df.Category == Category)]

    ## calculate cumsum
    df = df.sort_values('Date')
    df['CumSum'] = df.Amount.cumsum()

    ## following was an attempt to get new window to open with plot
    ## plt.switch_backend('AtQgg4')

    ## following was an attempt to fix missing plots in interactive window
    ## from IPython import get_ipython
    ## get_ipython().run_line_magic('matplotlib', 'inline')

    fig, ax = plt.subplots(figsize=figsize)
    sns.lineplot(ax=ax, data=df, x='Date', y='Amount', markers=',',
                 errorbar=None)\
       .set(title=Category)
    sns.lineplot(ax=ax, data=df, x='Date', y='CumSum', markers='o',
                 errorbar=None)
    ## sns.plot.show()
    ## plt.show()

    ## including this line also keeps function from plotting to screen in interactive
    ## maybe do outside the function instead
    ## plt.close('all')   

    ## the following does the same
    ## plt.close()

    df = df[['Date', 'AccountNum', 'Amount', 'CumSum']]

    return df

## plotb = plotcsv('In', 'Contributions', 'actualb.csv')
## plotc = plotcsv('In', 'Contributions', 'actualc.csv')

