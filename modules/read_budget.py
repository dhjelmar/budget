def read_budget(yearb):
    ## READ BUDGET DATA INTO DATAFRAME: budget

    # %%

    import pandas as pd
    import sys

    budgetfile = 'input_files/budget_' + str(yearb) + '.xlsx'
    alternate = input('Press enter to use following for budget: ' + budgetfile)
    if alternate != "":
        budgetfile = alternate
    print('budget file     :', budgetfile)
    
    ## read budget file
    budget = pd.read_excel(budgetfile)
    ## budget.columns = budget.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
    
    ## only keep needed columns
    budget = budget[['Account', 'Budget']]
    
    ## strip leading and trailing white space
    budget['Account'] = budget['Account'].str.strip()    

    ## create another column with budget line item number only because database not consistent with descriptions
    budget['AccountNum'] = budget.Account.str.extract('(^\d+a|^\d+)')

    ## rename Account column
    budget.columns = ['Accounta', 'Budget', 'AccountNum']
    
    ## drop any zero value or na
    budget = budget[budget.Budget != 0]
    budget = budget.dropna(subset = ['Budget'])
    #mask = budget[budget.Budget != 0 ].all(axis=1)]   # this seems to create a mask
    print(budget.head())

    # check for non-unique account numbers
    df = budget.AccountNum
    dups = df[df.duplicated()]
    if (len(dups) != 0):
        print('')
        print('FATAL ERROR: Duplicate Account numbers in budget file')
        print('duplicates:')
        print(dups)
        sys.exit()

    return budget, dups
