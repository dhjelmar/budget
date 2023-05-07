def plotit(df, x, y, hue=None, style=None, errorbar=None, title=None, filename=None):
    import pandas as pd
    import seaborn as sns
    from matplotlib import pyplot as plt
    sns.lineplot(data=df, x=x, y=y, hue=hue, style=style, errorbar=errorbar)\
        .set(title=title)       # this creates the figure
    if filename != None: { plt.savefig(filename) } # this write the figure to file filename
    plt.figure()                                  # this plots and closes the figure
