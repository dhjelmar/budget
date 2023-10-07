import datetime as dt
import pandas as pd
from modules.plotit import plotit

def category_plot(inout, category, budgettotals, 
                  startb, endb, actualb, actualc_adj, 
                  hue_order, markers, palette, path, fignum, figsize,
                  xlim=None, ylim=None):
    ## extract budget value
    budget_value = budgettotals.loc[(inout, category), 'Budget']
    budget_plot = pd.DataFrame({"Date":[startb, dt.date(endb.year, 12, 31)],
                                "Amount": [0, budget_value],
                                "Legend": ['Budget', 'Budget']})

    ## extract actualb values
    ## It would be better to not have to use inout but the combination is used.
    ## For the most part this works fine but it can fail with Xbudget category
    ## because that can be in or out
    if category == 'Xbudget':
        actualb_plot = actualb.loc[actualb['Category'] == category,:].copy()
    else:
        actualb_plot = actualb.loc[(actualb['InOrOut'] == inout) & (actualb['Category'] == category),:].copy()
    actualb_plot = actualb_plot[['Date', 'Amount']]
    if len(actualb_plot) > 0:
        actualb_plot = actualb_plot.sort_values('Date')
        actualb_plot['Amount'] = actualb_plot['Amount'].cumsum()
        actualb_plot['Legend'] = 'YTD'
    else:
        ## create dataframe from list
        data = {'Date'  : [startb],
                'Amount': [0],
                'Legend': ['YTD']}
        actualb_plot = pd.DataFrame(data)

    ## extract actual values from comparison year
    if category == 'Xbudget':
        actualc_plot = actualc_adj.loc[actualc_adj.Category == category,:].copy()
    else:
        actualc_plot = actualc_adj.loc[(actualc_adj.InOrOut == inout) & (actualc_adj.Category == category),:].copy()
    actualc_plot = actualc_plot[['Date', 'Amount']]
    if len(actualc_plot) > 0:
        actualc_plot = actualc_plot.sort_values('Date')
        actualc_plot['Amount'] = actualc_plot['Amount'].cumsum()
        actualc_plot['Legend'] = 'Last year'
    else:
        ## create dataframe from list
        data = {'Date'  : [startb],
                'Amount': [0],
                'Legend': ['Last year']}
        actualc_plot = pd.DataFrame(data)

    ## combine dataframes for plotting
    ## rbind = pd.concat([df1, df2], axis=0)
    df_plot = pd.concat([budget_plot, actualb_plot, actualc_plot], axis=0)

    expense_positive = False
    if expense_positive == True:
        ## if an expense category, plot as positive
        if inout == 'Out':
            df_plot.Amount = -1 * df_plot.Amount

    ## create plot
    filename = "category_{0:01d}".format(fignum)
    plotit(x='Date', y='Amount', data=df_plot, vline=endb, 
        hue='Legend', hue_order=hue_order, legendloc='best',
        style='Legend', markers=markers, palette=palette, 
        errorbar=None, title=inout + ": " + category, filename=path+filename+'_plot.png', figsize=figsize,
        xlim=xlim, ylim=ylim)

    return df_plot