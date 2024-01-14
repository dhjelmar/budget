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

    default = input('Press enter or escape for default to use current and prior year budget and comparison.\n'
                    '(If January, default will be prior year and year before that.)\n'
                    'Enter "x" (or anything else) to set start and end dates.')
    if default == "":

        ## create date variables
        today = dt.date.today()
        month = today.month

        if month == 1:
            ## month is January so default is to look at last year
            ## budget year is prior year
            yearb = today.year-1
            ## comparison year is  year before that
            yearc = today.year-2
            ## adder to yearb in later endb calculation
            adder = 1

        else:
            ## budget year is current year
            yearb = today.year
            ## comparison year is year before that
            yearc = today.year-1
            ## adder to yearb in later endb calculation
            adder = 0

        ## budget year
        startb = dt.date(yearb, 1, 1)
        # last day of prior month = 1st day of current month - 1 day
        endb   = dt.date(yearb + adder, month, 1) - dt.timedelta(days=1)
        ## comparison year
        startc = dt.date(yearc, 1, 1)
        endc   = dt.date(yearc, 12, 31)

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
