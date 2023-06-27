def tableit(map, budget, actualb, actualc, 
            startb, endb, startc):
    '''
    '''
    import pandas as pd
    import numpy as np
    import jellyfish
    from modules.mapit import mapit
    from modules.dateeom import dateeom
    from modules.linearadj import linearadj
    from modules.highlight import highlight

    ## prior month expenses
    actualbm = dateeom(actualb.copy())
    actualbm = actualbm.loc[actualbm['Date'] == endb]
    actualbm

    # %%
    ## for year to date summations, create new dataframes stripping actualc to same duration as actualb
    ytdb = actualb.copy()
    ytdc = actualc.copy()
    ytdc = ytdc.loc[(actualc['Date'] >= startc) & (actualc['Date'] <= (startc + (endb - startb)))]

    # %%
    ## use pivot table to sum ytd and current month totals
    ytdb = ytdb.pivot_table(index=['AccountNum'], values='Amount', aggfunc=np.sum).reset_index()
    ytdb.columns = ['AccountNum', 'YTD']
    ytdc = ytdc.pivot_table(index=['AccountNum'], values='Amount', aggfunc=np.sum).reset_index()
    ytdc.columns = ['AccountNum', 'Last YTD']
    actualbm = actualbm.pivot_table(index=['AccountNum'], values='Amount', aggfunc=np.sum).reset_index()
    actualbm.columns = ['AccountNum', 'Current Month']
    # temp.loc[temp.AccountNum == '4044']

    # %%
    ## full, outer join (i.e., include any line item in any dataframe) for budget, ytdb, and ytdc
    temp = budget.loc[:, ['AccountNum', 'Budget']]
    temp = pd.merge(temp, ytdb, how='outer', on='AccountNum')
    # temp.loc[temp.AccountNum == '4044']
    temp = pd.merge(temp, ytdc, how='outer', on='AccountNum')
    # temp.loc[temp.AccountNum == '4044']
    all = pd.merge(temp, actualbm, how='outer', on='AccountNum')
    all = all.fillna(0)
    all.AccountNum = all.AccountNum.astype(str)
    all.index = range(len(all))

    # %%
    ## left join with mapit
    all, missing = mapit(all, map)

    # %%
    ## select columns to keep
    table = all.loc[:, ['InOrOut', 'Category', 'Account', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'SourceOfFunds', 'AccountNum']].copy()

    # %%
    ## eliminate any rows in table where all entries are $0
    #mask = (table.Budget != 0) & (table.YTD != 0) & (table['Last YTD'] != 0) & (table['Current Month'] != 0)
    mask = (table.Budget == 0) & (table.YTD == 0) & (table['Last YTD'] == 0) & (table['Current Month'] == 0)
    table = table[-mask].copy()
    table.index = range(len(table))

    # %%
    '''
    ## add column for YTD percent
    table['YTD%'] = table['YTD'] / table['Budget'] * 100
    ## replace nan, inf, and -inf with 999
    table['YTD%'] = table['YTD%'].replace([np.nan, np.inf, -np.inf], 999, inplace=True)
    ## round to integer
    table['YTD%'] = table['YTD%'].round(0).astype(int)
    ## replace 999 with inf
    table['YTD%'] = table['YTD%'].replace([999], np.inf, inplace=True)
    '''

    # %%
    ## sort table and add a flag for changes to category
    ##table = table.sort_values(by = ['Account', 'Category', 'InOrOut'], ascending=True, na_position='last')
    table = table.sort_values(by = ['InOrOut', 'Category', 'Account'], ascending=True, na_position='last')
    i = table.Category    
    table['flag'] = i.ne(i.shift()).cumsum() % 2
    table.style.apply(highlight, axis=1)

    return table