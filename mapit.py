def mapit(dataframe, map):
    '''
    pd.merge(dataframe, map, how='left', on='AccountNum')
    '''

    import pandas as pd
    import regex as re

    df = dataframe.copy()
    df = pd.merge(df, map, how='left', on='AccountNum')

    ## flag any line items from budget without Category assigned
    nan_values = df[df['Category'].isna()]
    if len(nan_values) != 0:
    #    print('')
    #    print('FATAL ERROR: Following budget entries are missing a Category assignment in map.xlsx file')
    #    print(nan_values)
    #    sys.exit()

        ## classify anything that does not have Category defined in map
        mask = df['Category'].isna()
        df.loc[mask, 'Category'] = 'Xbudget'
        df.loc[mask, 'GreenSheet'] = 'Xbudget'
        df.loc[mask, 'Committee'] = 'Xbudget'
        df.loc[mask, 'SourceOfFunds'] = 'Xbudget'
        
        ## set InOrOut based on dollar fields being positive or negative
        dollarfields = [x for x in df.columns if re.findall(r'Amount',x)]
        df['dollarsum'] = 0   # initialize new variable
        for i in dollarfields:
            df.loc[mask, 'dollarsum'] = df.loc[mask, 'dollarsum'] + df.loc[mask, i]
        df.loc[(df.InOrOut.isna() & df.dollarsum >= 0), 'InOrOut'] = 'In' 
        df.loc[(df.InOrOut.isna() & df.dollarsum <  0), 'InOrOut'] = 'Out' 


    print(df)

    return df, nan_values
