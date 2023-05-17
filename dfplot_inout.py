def dfplot_inout(map, table, actualb, actualc_adj, 
                 startb, endb, startc, endc):
    '''
    '''
    import pandas as pd
    import numpy as np
    import datetime as dt
    from mapit import mapit

    # %% [markdown]
    ## Create plot for all income and expenses

    # %% 

    ## create budget in/out dataframe
    endb_year = dt.date(endb.year, 12, 31)
    df = table.copy()
    df = df.groupby('InOrOut')['Budget'].sum().abs()
    df = pd.DataFrame({"Date":[startb, endb_year, startb, endb_year],
                    "Amount": [0, df['In'], 0, df['Out']],
                    "InOrOut": ['In', 'In', 'Out', 'Out']})
    df['Legend'] = 'Budget'
    budget_inout = df.copy()

    # %%

    ## create same dataframe for budget year Income and Expenses
    df, junk = mapit(actualb, map)
    df = df.pivot_table(index=['InOrOut', 'Date'], values='Amount', aggfunc=np.sum).reset_index()
    df.Amount = df.Amount.abs()
    df.Amount = df.groupby('InOrOut')['Amount'].cumsum()
    df['Legend'] = 'YTD'
    actualb_inout = df.copy()

    ## create same dataframe for comparison year Income and Expenses
    df, junk = mapit(actualc_adj, map)
    df = df.pivot_table(index=['InOrOut', 'Date'], values='Amount', aggfunc=np.sum).reset_index()
    df.Amount = df.Amount.abs()
    df.Amount = df.groupby('InOrOut')['Amount'].cumsum()
    df['Legend'] = 'Prior year'
    actualc_inout = df.copy()

    ## combine
    df_plots = pd.concat([budget_inout, actualb_inout, actualc_inout], axis=0)

    return df_plots