def linearadj(filename, dfin, start, end):
    '''
    Read filename to...
    '''
    import pandas as pd
    import numpy as np
    from date_eom import date_eom
    from dateeom import dateeom

    # %%
    df = dfin.copy()

    ## monthly cumsum for df and dfc then flatten
    df = dateeom(df)
    df = df.pivot_table(index=['AccountNum', 'Account', 'Date'], values=['Amount'], aggfunc=np.sum) # cumsum
    df = df.reset_index()    # flatten

    # %%
    ## read budget_linear.xlsx
    linear = pd.read_excel(filename)
    linear.AccountNum = linear.AccountNum.astype(str)
    linear_list = list(linear.AccountNum.unique())

    ## determine correct columns from linear for budgetb and budgetc and redefine linear dataframe
    budget = linear['budget'+str(start.year)]
    linear = pd.DataFrame({'AccountNum' : linear.AccountNum, 
                           'budget'     : budget})

    # %%
    ## expand linear to have an entry for each AccountNum for each month
    dicts = []
    for AccountNum in linear_list:
        for month in range(1,13):
            if month > end.month:
                break           # exit for loop
            eom = date_eom(start.year, month)
            ## values[0] is needed in the following to remove the value from a series
            amount = linear.loc[linear.AccountNum == AccountNum, 'budget'].values[0] * month/12
            dicts.append(
                {
                    'Date': eom,
                    'Account': AccountNum + ' linear adjustment',
                    'Amount': amount,
                    'AccountNum': AccountNum
                }
            )
    linear2 = pd.DataFrame(dicts)

    # %%
    ## combine, sort, and renumber
    df = pd.concat([df, linear2], axis=0)  # rbind
    df = df.sort_values(by = ['AccountNum', 'Date'], ascending=True, na_position='last')  # sort
    df.index = range(len(df))              # renumber dataframe

    return df