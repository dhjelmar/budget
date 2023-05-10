def set_dates():
    '''
    Set budget and comparison year start and end dates

    Input:  Keyboard input (format: mm/dd/yyyy)
            default startb = January 1st of current year
                    endb   = Last day of prior month
                    startc = January 1st of prior year
                    endc   = December 31st of prior year

    Output: startb, endb = start and end dates for budget year
            startc, endc = start and end dates for comparison year
    '''

    import datetime as dt
    
    # %%
    ## https://towardsdatascience.com/working-with-datetime-in-pandas-dataframe-663f7af6c587

    default = input('Press enter or escape to use current and prior year budget and comparison.\n'
                    'Enter "x" (or anything else) to set start and end dates.')
    if default == "":
        ## budget year to end of prior month
        startb = dt.date(dt.date.today().year, 1, 1)
        endb   = dt.date(dt.date.today().year, dt.date.today().month, 1) - dt.timedelta(days=1)
        ## comparison year
        startc = dt.date(dt.date.today().year-1, 1, 1)
        endc   = dt.date(dt.date.today().year-1, 12, 31)

    else:
        startb = input('Enter start date for budget     year (mm/dd/yyyy):')
        endb   = input('Enter end   date for budget     year (mm/dd/yyyy):')
        startc = input('Enter start date for comparison year (mm/dd/yyyy):')
        endc   = input('Enter end   date for comparison year (mm/dd/yyyy):')

        ## convert to dates
        startb = dt.datetime.strptime(startb, '%m/%d/%Y').date()
        endb   = dt.datetime.strptime(endb  , '%m/%d/%Y').date()
        startc = dt.datetime.strptime(startc, '%m/%d/%Y').date()
        endc   = dt.datetime.strptime(endc  , '%m/%d/%Y').date()

    print('budget start    :', startb)
    print('budget end      :', endb)
    print('comparison start:', startc)
    print('comparison end  :', endc)

    return startb, endb, startc, endc
