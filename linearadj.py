def linearadj(filename, table, startb, startc, endb):
    '''
    Read filename to...
    '''
    df = table.copy()
    import pandas as pd
    ## read budget_linear.xlsx
    linear = pd.read_excel(filename)
    linear.AccountNum = linear.AccountNum.astype(str)

    ## apply map
    ## linear, missing = mapit(linear, map)

    ## pull corresponding lines from df
    ## dfvals = df.loc[df['AccountNum'].isin(linear.AccountNum)].copy()

    ## pull corresponding lines from df
    linear = pd.merge(linear, df, how='left', on='AccountNum')

    ## determine YTD for linear adjustments
    budgetb = linear['budget'+str(startb.year)]
    budgetc = linear['budget'+str(startc.year)]
    linear['Current Month'] = round(budgetb              / 12 - linear['Current Month'], 2)
    linear['Last YTD']      = round(budgetc              / 12 - linear['Last YTD'], 2)
    linear.YTD              = round(budgetb * endb.month / 12 - linear.YTD, 2)
    linear.Budget           = 0
    linear.Account = linear['AccountNum'].astype(str) + " linear adjustment"

    ## only keep same columns from linear as had in df so can combine
    linear = linear[df.columns]

    ## add to df
    ## rbind = pd.concat([df1, df2], axis=0)
    df = pd.concat([df, linear], axis=0)
    df.index = range(len(df))

    return df