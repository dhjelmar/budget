def convert(yearb, columns=['Account', 'Budget_2024', 'Source_of_Funds', 'Recurring', 'Budget_2023', 'Current_Balance', 'Difference', 'Comments'],
            dollar_columns=[2,5]):
    ## READ OFFICE VERSION OF BUDGET DATA INTO DATAFRAME: budget

    import pandas as pd
    import numpy as np

    budgetfile = 'input_files/budget_' + str(yearb) + '_office.xlsx'
    #alternate = input('Press enter to use following for budget: ' + budgetfile)
    #if alternate != "":
    #    budgetfile = alternate
    print('budget file     :', budgetfile)
    
    ## read budget file and fix column names
    df = pd.read_excel(budgetfile)
    if (columns == None):
        ## use column names from Excel but replace special characters with "_"
        df.columns = df.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
        columns = df.columns
    else:
        df.columns = columns

    ## remove any row where Source_of_Funds is NaN
    df = df.dropna(subset = ['Source_of_Funds'])

    ## create another column with budget line item number only because database not consistent with descriptions
    df['AccountNum'] = df.Account.str.extract('(^\d+a|^\d+)')
    df['AccountNum'] = pd.to_numeric(df['AccountNum'])
    ## type(df.iloc[0]['AccountNum'])

    ## create column indicating whether account is income (In) or expense (Out)
    df['InOrOut'] = np.where(df['AccountNum'] < 5000, 'In', 'Out')
    for i in dollar_columns:
        df.iloc[:,i] = np.where(df['InOrOut'] == 'In', df.iloc[:,i], -df.iloc[:,i])

    ## move InOrOut and AccountNum to front of dataframe
    newcols = ['InOrOut'] + ['AccountNum'] + columns
    df = df[newcols]

    return df

budget = convert(2024)
budget[['InOrOut', 'AccountNum', 'Account', 'Budget_2023', 'Budget_2024']]