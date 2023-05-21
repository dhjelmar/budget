def plotit(df, x, y, hue=None, style=None, errorbar=None, title=None, filename=None, figsize=(6,4)):
    import pandas as pd
    import seaborn as sns
    from matplotlib import pyplot as plt

    #if layout == 'ALT':
    #    sns.set(rc={'figure.figsize':(7,2)})
    #sns.lineplot(data=df, x=x, y=y, hue=hue, style=style, errorbar=errorbar)\
    #   .set(title=title)
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.lineplot(ax=ax, data=df, x=x, y=y, hue=hue, style=style, errorbar=errorbar)\
       .set(title=title)

    if filename != None: { plt.savefig(filename) } # this write the figure to file filename
    plt.figure()                                  # this plots and closes the figure



# import pandas as pd
# df = pd.DataFrame({'col1': [1,2,3,4],
#                    'col2': [10,15,10,12],
#                    'label': ['one', 'two', 'one', 'two']})
# plotit(df, 'col1', 'col2', hue='label')
# plotit(df, 'col1', 'col2', hue='label', figsize=(8,2))