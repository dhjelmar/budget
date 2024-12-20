import modules as my

def inconsistent(map, budget, actualb, actualc, 
            startb, endb, startc):
    '''
    '''
    import pandas as pd
    import numpy as np
    import jellyfish
    from modules.mapit import mapit
    from modules.dateeom import dateeom

    # budget year
    budget_year = str(actualb.Date[0].year)

    # create dataframe of all Icon entries
    actualb = actualb[['Date', 'Account_Icon', 'AccountNum']]
    actualc = actualc[['Date', 'Account_Icon', 'AccountNum']]
    all = pd.concat([actualc, actualb], axis=0, ignore_index=True)         # rbind

    # merge budget account names
    budget = budget[['Account_Budget', 'AccountNum']]
    all = pd.merge(all, budget, how='left', on='AccountNum')

    # merge map account names
    map = map[['Account', 'AccountNum']]
    map.columns = ['Account_Map', 'AccountNum']
    all = pd.merge(all, map, how='left', on='AccountNum')

    ## Check actual for mismatched account names
    mismatched_dict = []
    for row in range(len(all)):
        a = jellyfish.jaro_similarity(str(all.loc[row,'Account_Map']), str(all.loc[row,'Account_Budget']))
        b = jellyfish.jaro_similarity(str(all.loc[row,'Account_Map']), str(all.loc[row,'Account_Icon']))
        similar = min(a,b)
        if similar < 1:
            ## not 100% similar so add to mismatched_dict
            mismatched_dict.append(
                {
                    'Date': all.loc[row,'Date'],
                    'AccountNum': all.loc[row,'AccountNum'],
                    'Similar': similar,
                    'Account_Map': all.loc[row,'Account_Map'],
                    'Account_Budget_'+budget_year: all.loc[row,'Account_Budget'],
                    'Account_Icon': all.loc[row,'Account_Icon'],
                }
            )
    inconsistencies = pd.DataFrame(mismatched_dict)
    inconsistencies = inconsistencies.sort_values('Similar')

    return inconsistencies


    '''
    ### prior month expenses
    #actualbm = dateeom(actualb.copy())
    #actualbm = actualbm.loc[actualbm['Date'] == endb]
    #actualbm

    # %%
    ## for year to date summations, create new dataframes stripping actualc to same duration as actualb
    ytdb = actualb.copy()
    ytdc = actualc.copy()
    ytdc = ytdc.loc[(actualc['Date'] >= startc) & (actualc['Date'] <= (startc + (endb - startb)))]

    # %%
    ## use pivot table to sum ytd and current month totals
    ## pivot = budget.pivot_table(index=['InOrOut', 'Committee', 'GreenSheet'], values='Budget', aggfunc=np.sum)
    ytdb = ytdb.pivot_table(index=['AccountNum', 'Account_Icon'], values='Amount', aggfunc=np.sum).reset_index()
    ytdb.columns = ['AccountNum', 'Account_Icon_b', 'YTD']
    ytdc = ytdc.pivot_table(index=['AccountNum', 'Account_Icon'], values='Amount', aggfunc=np.sum).reset_index()
    ytdc.columns = ['AccountNum', 'Account_Icon_c', 'Last YTD']
    #actualbm = actualbm.pivot_table(index=['AccountNum', 'Account'], values='Amount', aggfunc=np.sum).reset_index()
    #actualbm.columns = ['AccountNum', 'Accountbm', 'Current Month']
    # temp.loc[temp.AccountNum == '4044']

    # %%
    ## full, outer join (i.e., include any line item in any dataframe) for budget, ytdb, and ytdc
    temp = budget.loc[:, ['AccountNum', 'Accounta', 'Budget']]
    temp = pd.merge(temp, ytdb, how='outer', on='AccountNum')
    # temp.loc[temp.AccountNum == '4044']
    temp = pd.merge(temp, ytdc, how='outer', on='AccountNum')
    # temp.loc[temp.AccountNum == '4044']
    #all = pd.merge(temp, actualbm, how='outer', on='AccountNum')
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
        a = jellyfish.jaro_similarity(str(all.loc[row,'Account']), str(all.loc[row,'Accounta']))
        b = jellyfish.jaro_similarity(str(all.loc[row,'Account']), str(all.loc[row,'Accountb']))
        c = jellyfish.jaro_similarity(str(all.loc[row,'Account']), str(all.loc[row,'Accountc']))
        similar = min(a,b,c)
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


    return inconsistencies

    '''