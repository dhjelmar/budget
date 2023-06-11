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
    actualb_plot = actualb.loc[(actualb['InOrOut'] == inout) & (actualb['Category'] == category),:].copy()
    actualb_plot = actualb_plot[['Date', 'Amount']]
    actualb_plot = actualb_plot.sort_values('Date')
    actualb_plot['Amount'] = actualb_plot['Amount'].cumsum()
    actualb_plot['Legend'] = 'YTD'

    ## extract actual values from comparison year
    actualc_plot = actualc_adj.loc[(actualc_adj.InOrOut == inout) & (actualc_adj.Category == category),:].copy()
    actualc_plot = actualc_plot[['Date', 'Amount']]
    actualc_plot = actualc_plot.sort_values('Date')
    actualc_plot['Amount'] = actualc_plot['Amount'].cumsum()
    actualc_plot['Legend'] = 'Last year'

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