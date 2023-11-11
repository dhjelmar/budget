#%%
def convert(file='../input_files/budget_2024_office.xlsx',
            col_rename=['Account', 'Budget_2024', 'Source_of_Funds', 'Recurring', 'Budget_2023', 'Current_Balance', 'Difference', 'Comments'],
            budget_columns=[1,4],
            col_out   =['InOrOut', 'AccountNum', 'Account', 'Budget_2024']):
    ## READ OFFICE VERSION OF BUDGET DATA INTO DATAFRAME: df

    import pandas as pd
    import numpy as np

    ## read budget file and fix column names
    df = pd.read_excel(file)
    df.columns = col_rename

    ## remove any row where Source_of_Funds is NaN
    df = df.dropna(subset = ['Source_of_Funds'])

    ## create another column with budget line item number only because database not consistent with descriptions
    df['AccountNum'] = df.Account.str.extract('(^\d+a|^\d+)')
    df['AccountNum'] = pd.to_numeric(df['AccountNum'])
    ## type(df.iloc[0]['AccountNum'])

    ## create column indicating whether account is income (In) or expense (Out)
    df['InOrOut'] = np.where(df['AccountNum'] < 5000, 'In', 'Out')
    df['AccountNum'] = df['AccountNum'].apply(str) # convert back to string for merge later
    for i in budget_columns:
        df.iloc[:,i] = np.where(df['InOrOut'] == 'In', df.iloc[:,i], -df.iloc[:,i])

    ## move InOrOut and AccountNum to front of dataframe
    df = df[col_out]

    return df

#%%
budget = convert()

#%%
## read prior year
import pandas as pd
df = pd.read_excel('../input_files/budget_2023.xlsx')
df = df[['Account', 'Budget']]

#%%
df['AccountNum'] = df.Account.str.extract('(^\d+a|^\d+)')
df.columns = ['Account_2023', 'Budget_2023', 'AccountNum']


#%%
## merge dataframes (must be on sring)
dfnew = pd.merge(df, budget, how='outer', on='AccountNum')
dfnew = [['InOrOut', 'AccountNum', 'Account', 'Budget_2024', 'Account_2023', 'Budget_2023']]

