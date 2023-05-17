def tableit(map, budget, actualb, actualc, 
            startb, endb, startc, endc,
            apply_linear_adjustments):
    '''
    '''
    import pandas as pd
    import numpy as np
    import jellyfish
    from mapit import mapit
    from dateeom import dateeom
    from linearadj import linearadj
    from highlight import highlight

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
    ## pivot = budget.pivot_table(index=['InOrOut', 'Committee', 'GreenSheet'], values='Budget', aggfunc=np.sum)
    ytdb = ytdb.pivot_table(index=['AccountNum', 'Account'], values='Amount', aggfunc=np.sum).reset_index()
    ytdb.columns = ['AccountNum', 'Accountb', 'YTD']
    ytdc = ytdc.pivot_table(index=['AccountNum', 'Account'], values='Amount', aggfunc=np.sum).reset_index()
    ytdc.columns = ['AccountNum', 'Accountc', 'Last YTD']
    actualbm = actualbm.pivot_table(index=['AccountNum', 'Account'], values='Amount', aggfunc=np.sum).reset_index()
    actualbm.columns = ['AccountNum', 'Accountbm', 'Current Month']


    # %%

    ## full, outer join (i.e., include any line item in any dataframe) for budget, ytdb, and ytdc
    temp = budget.loc[:, ['AccountNum', 'Accounta', 'Budget']]
    temp = pd.merge(temp, ytdb, how='outer', on='AccountNum')
    temp = pd.merge(temp, ytdc, how='outer', on='AccountNum')
    all = pd.merge(temp, actualbm, how='outer', on='AccountNum')
    all = all.fillna(0)
    all.AccountNum = all.AccountNum.astype(str)
    all.index = range(len(all))


    # %%
    ## left join with mapit
    all, missing = mapit(all, map)


    # %% [markup]
    ## Check actual for mismatched account names
    mismatched_dict = []
    for row in range(len(all)):
        a = jellyfish.jaro_distance(str(all.loc[row,'Account']), str(all.loc[row,'Accounta']))
        b = jellyfish.jaro_distance(str(all.loc[row,'Account']), str(all.loc[row,'Accountb']))
        c = jellyfish.jaro_distance(str(all.loc[row,'Account']), str(all.loc[row,'Accountc']))
        similar = max(a,b,c)
        if similar < 1:
            ## not 100% similar so add to mismatched_dict
            mismatched_dict.append(
                {
                    'AccountNum': all.loc[row,'AccountNum'],
                    'Similar': similar,
                    'Account': all.loc[row,'Account'],
                    'Account_budget': all.loc[row,'Accounta'],
                    'Account_actualb': all.loc[row,'Accountb'],
                    'Account_actualc': all.loc[row,'Accountc'],
                }
            )
    inconsistencies = pd.DataFrame(mismatched_dict)


    # %%
    ## select columns to keep
    table = all.loc[:, ['InOrOut', 'Category', 'Account', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'SourceOfFunds', 'AccountNum']].copy()


    # %% [markdown]
    ## Add adjustment entries for linear YTD income
    if apply_linear_adjustments == True:
        filename = 'budget_linear.xlsx'
        table = linearadj(filename, table, startb, startc, endb)


    # %%
    ## eliminate any rows in table where all entries are $0
    #mask = (table.Budget != 0) & (table.YTD != 0) & (table['Last YTD'] != 0) & (table['Current Month'] != 0)
    mask = (table.Budget == 0) & (table.YTD == 0) & (table['Last YTD'] == 0) & (table['Current Month'] == 0)
    table = table[-mask].copy()
    table.index = range(len(table))


    # %%
    ## sort table and add a flag for changes to category
    ##table = table.sort_values(by = ['Account', 'Category', 'InOrOut'], ascending=True, na_position='last')
    table = table.sort_values(by = ['InOrOut', 'Category', 'Account'], ascending=True, na_position='last')
    i = table.Category    
    table['flag'] = i.ne(i.shift()).cumsum() % 2
    table.style.apply(highlight, axis=1)

    return table, inconsistencies