def date_eom(year, month):
    '''
    find end of month given year and month
    '''
    import datetime as dt
    if month < 12:
        ## find start of next month then subtract 1 day
        eom = dt.date(year, month+1, 1) - dt.timedelta(days=1)
    else:
        ## if December, find start of next year then subtract 1 day
        eom = dt.date(year + 1, 1, 1) - dt.timedelta(days=1)

    return eom

## print(date_eom(2023, 1))
## print(date_eom(2023, 4))
## print(date_eom(2023, 12))
