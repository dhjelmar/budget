def dupacct(df) :
    '''
    check for non-unique account numbers

    input: df = dataframe

    output: dataframe of duplicate account numbers
    '''
    df = df.AccountNum.copy()
    dups = df[df.duplicated()]
    return dups