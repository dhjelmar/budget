def plotit(x, y, data, hue=None, hue_order=None, legendloc='best',
           style=None, markers=None, palette=None, errorbar=None, 
           title=None, filename=None, figsize=(6,4)):
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
    sns.lineplot(ax=ax, data=data, x=x, y=y, hue=hue, hue_order=hue_order,
                 style=style, markers=markers, palette=palette, errorbar=errorbar)\
       .set(title=title)
    
    plt.legend(loc=legendloc)
    
    if filename != None: { plt.savefig(filename) } # this write the figure to file filename
    plt.figure()                                  # this plots and closes the figure


def plotit_test():
    import pandas as pd
    df = pd.DataFrame({'col1': [1,2,3,4],
                       'col2': [10,15,10,12],
                       'label': ['one', 'two', 'one', 'two']})
    plotit('col1', 'col2', df, hue='label', style='label', 
           markers=[',', 'o', ','], palette=['b', 'g', 'r'], figsize=(8,2))
    plotit('col1', 'col2', df, hue='label', hue_order=['two', 'one'], style='label', 
           markers=[',', 'o', ','], palette=['b', 'g', 'r'], figsize=(8,2))

    #import seaborn as sns
    #sns.lineplot(x='col1', y='col2', data=df, 
    #             hue='label', style='label', markers=[",","o"])

# plotit_test()