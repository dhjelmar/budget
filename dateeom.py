def dateeom(dfin):
    '''
    In dataframe, dfin, pushes dates in column "Date" to month ends

    Input
    -----
        dfin = dataframe with one column "Date"
               "Date" can be most any format string or a pd.to_datetime() date

    Output
    ------
        df with "Date" converted to month ends

    Example
    -------
        dfout = dateeom(dfin)
    '''
    import pandas as pd
    import datetime as dt
    import calendar
    df = dfin.copy()
    df.Date = pd.to_datetime(df.Date)
    for i in range(0,len(df)):
        ## following works except for December
        ##    df.Date[i] = dt.date(df.Date[i].year, df.Date[i].month+1, 1) - dt.timedelta(days=1)
        ## following works better
        year = df.Date[i].year
        month = df.Date[i].month
        day = calendar.monthrange(year, month)[1]
        df.Date[i] = dt.date(year, month, day)
        df.at[i, 'Date'] = dt.date(year, month, day)

    df = df.reindex()

    return df
