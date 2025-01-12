import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

def select(df, InOrOut='all', L1='all', L2='all'):
    # initialize masks to True
    numdf = len(df)
    mask_InOrOut =[True] * numdf
    mask_L1 =[True] * numdf
    mask_L2 =[True] * numdf
    # set individual masks
    if InOrOut!='all':
        mask_InOrOut = df.InOrOut == InOrOut
    if L1 != 'all':
        mask_L1 = df.L1 == L1
    if L2 != 'all':
        mask_L2 = df.L2 == L2
    # combine masks and apply
    mask = mask_InOrOut * mask_L1 * mask_L2
    df = df[mask].copy()
    return df

def xycumsum(df, InOrOut='all', L1='all', L2='all', x='Date', y='Amount'):
    # cumsum value of y in df by InOrOut, L1, L2 and x
    # select requested rows of df
    df = select(df, InOrOut, L1, L2)
    # sum value in column y for each combination of index
    df = df.pivot_table(index=['InOrOut', 'L1', 'L2', x], values=y, aggfunc='sum').reset_index()
    # sort by x
    df = df.sort_values(x)
    # cumulative sumation
    #df[y] = df.groupby('InOrOut')[y].cumsum()  # similar to below but less straight forward
    df[y] = df[y].cumsum()
    df['Legend'] = L1 + '; ' + L2
    return df

def plot_compare(InOrOut, L1, L2, endb, actualb, actualc_adj, table, path):
    dfb_ytd = xycumsum(actualb    , InOrOut, L1, L2)
    dfc_adj = xycumsum(actualc_adj, InOrOut, L1, L2)
    title = InOrOut + '; ' + L1 + '; ' + L2 + ' as of ' + str(endb)
    ax = dfb_ytd.plot(x='Date', y='Amount', label='budget YTD', title=title)
    dfc_adj.plot(x='Date', y='Amount', label='comparison year', linestyle='--', ax=ax)
    # add date for table
    year = endb.year
    table['Date'] = dt.date(year, 12, 31)
    dfb_budget = xycumsum(table, InOrOut, L1, L2, x='Date', y='Budget')
    if len(dfb_budget) > 1:
        # only keep the last row
        dfb_budget = dfb_budget.tail(1).reset_index()
    # add new 1st row
    dfb_budget = pd.concat([dfb_budget, dfb_budget.loc[[0]]], ignore_index=True)
    # change date and value of 1st row
    dfb_budget.loc[0,'Date'] = dt.date(year, 1, 1)
    dfb_budget.loc[0,'Budget'] = 0
    dfb_budget.plot(x='Date', y='Budget', label='budget', ax=ax)
    if path != None: { plt.savefig(path) } # this write the figure to file path
    plt.figure()                           # this plots and closes the figure
    return dfb_ytd