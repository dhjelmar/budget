def mapit(dataframe, map):
    '''
    pd.merge(dataframe, map, how='left', on='AccountNum')
    '''

    import pandas as pd
    df = dataframe.copy()
    df = pd.merge(df, map, how='left', on='AccountNum')

    ## flag any line items from budget without Category assigned
    nan_values = df[df['Category'].isna()]
    if len(nan_values) != 0:
        print('')
        print('FATAL ERROR: Following budget entries are missing a Category assignment in map.xlsx file')
        print(nan_values)
        sys.exit()

    print(df)

    return df, nan_values
