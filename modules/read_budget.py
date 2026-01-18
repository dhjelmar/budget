import os

def read_budget(yearb):
    ## READ BUDGET DATA INTO DATAFRAME: budget

    # %%

    import pandas as pd
    import sys

    budgetfile = os.path.join('input', 'budget.xlsx')
    
    ## read budget file
    budget = pd.read_excel(budgetfile)
    ## budget.columns = budget.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
    
    ## only keep needed columns
    budget = budget[['Year', 'Account', 'Budget']]
    
    ## strip leading and trailing white space
    budget['Account'] = budget['Account'].str.strip()    

    ## create another column with budget line item number only because database not consistent with descriptions
    budget['AccountNum'] = budget.Account.str.extract('(^\d+a|^\d+)')

    ## rename Account column
    budget.columns = ['Year', 'Account', 'Budget', 'AccountNum']
    
    ## drop any zero value or na
    budget = budget[budget.Budget != 0]
    budget = budget.dropna(subset = ['Budget'])
    #mask = budget[budget.Budget != 0 ].all(axis=1)]   # this seems to create a mask
    #print(budget.head())

    ## sum budget value if every other column is a match
    ## this allows for adding budget rows if needed for late year additions
    ## still flags as an error if anything is different in Year, Account, or AccountNum
    match_columns = ['Year', 'Account', 'AccountNum']
    target_column = 'Budget'
    matches = budget[match_columns].apply(lambda row: tuple(row.dropna().unique()), axis=1)
    budget = budget.groupby(matches)[target_column].sum().reset_index()
    # groupby creates a tuple column named 'index' that needs to get pulled apart again
    budget.columns = ['stuff', 'Budget']
    budget[match_columns] = budget['stuff'].apply(pd.Series)
    budget = budget.drop(columns='stuff')
    budget = budget[['Year', 'Account', 'Budget', 'AccountNum']]

    # check for non-unique account numbers
    years = list(dict.fromkeys(budget.Year))
    for year in years:
        df = budget.loc[budget.Year==year].AccountNum
        dups = df[df.duplicated()]
        if (len(dups) != 0):
            print('')
            print('FATAL ERROR: Duplicate Account numbers in budget file')
            print('duplicates:')
            print(dups)
            sys.exit()

    return budget, dups
