#%%
import pandas as pd
import numpy as np
from datetime import datetime as dt
from modules.read_map import read_map
from modules.mapit import mapit

def convert(file='input_files/budget_2024_office.xlsx',
            col_rename=['Account', 'Budget', 'Source_of_Funds', 'Recurring', 'Budget_2023', 'Current_Balance', 'Difference', 'Comments'],
            budget_columns=[1,4],
            year=2024,
            col_out   =['Year', 'Date', 'InOrOut', 'AccountNum', 'Account', 'Budget']):
    ## READ OFFICE VERSION OF BUDGET DATA INTO DATAFRAME: df

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

    ## add year and date columns
    df['Year'] = year
    ## df['Date'] = dt.today().strftime('%Y-%m-%d')
    today = dt.today().strftime('%m/%d/%y')
    ## df['Date'] = dt.strptime(today, '%m/%d/%y')
    df['Date'] = 'Budget ' + str(year) + ' (' + today + ')'

    ## move InOrOut and AccountNum to front of dataframe
    df = df[col_out]

    return df

#%%
budget = convert()

#%%
## read prior years
df = pd.read_excel('input_files/budget_all.xlsx')

## combine into single dataframe
df = pd.concat([df, budget], axis=0)

#%% 
## map to categories
map, map_duplicates = read_map()

## first need to convert AccountNum to string for merge operation
df['AccountNum'] = df['AccountNum'].apply(str)
dfmapped, missing = mapit(df, map)

#%%
dfmapped.columns = ['Year', 'Date', 'InOrOut_x', 'AccountNum', 'Account_x', 'Budget',
                    'InOrOut_y', 'Category', 'SourceOfFunds', 'Account', 'InOrOut',
                    'dollarsum']

## reorder columns and only keep some columns
dfmapped = dfmapped[['Year', 'Date', 'InOrOut', 'AccountNum', 'Account', 'Budget', 'Category', 'SourceOfFunds', 'InOrOut_x', 'Account_x']]

# %%
## write to Excel
dfmapped.to_excel('convert_out.xlsx', index=False)



##################################################

##%%
### read prior year
#import pandas as pd
#df = pd.read_excel('input_files/budget_2023.xlsx')
#df = df[['Account', 'Budget']]
#
##%%
#df['AccountNum'] = df.Account.str.extract('(^\d+a|^\d+)')
#df.columns = ['Account_2023', 'Budget_2023', 'AccountNum']
#
#
##%%
### merge dataframes (must be on sring)
#dfnew = pd.merge(df, budget, how='outer', on='AccountNum')
#dfnew = [['InOrOut', 'AccountNum', 'Account', 'Budget_2024', 'Account_2023', 'Budget_2023']]


# %%
