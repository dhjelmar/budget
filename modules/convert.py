import pandas as pd
import numpy as np
from datetime import datetime as dt

def convert(file,
            col_acct=0,
            col_budget=1,
            year=2023,
            col_rename=['Account', 'Budget', 'Source_of_Funds'],
            col_out   =['Year', 'Description', 'InOrOut', 'AccountNum', 'Account', 'Budget', 'File']):
    '''
    CONVERT OFFICE VERSION OF BUDGET DATA TO PANDAS DATAFRAME
    input:  file = xlsx file in format used by office for developing budget
            col_account = column with account number; header used as 'Description'
            col_budget  = column with budget value for account
    output: dataframe with col_out columns
    '''
    ## read budget file and fix column names
    df = pd.read_excel('input_files/' + file)
    budget_header = df.columns[col_budget]
    ## drop all except 1st two columns
    #df1 = df.iloc[:, [0, 1]]
    # only keep two specified rows
    df1 = df.iloc[:, [col_acct, col_budget]]
    ## drop all except source of funds column
    df2 = df.loc[:, 'Source of Funds']
    ## merge back together and rename columns
    df = pd.concat([df1,df2], axis=1)
    df.columns = col_rename

    ## remove any row where Source_of_Funds is NaN
    ## this is important to strip out non-budget rows
    df = df.dropna(subset = ['Source_of_Funds'])

    ## create another column with budget line item number only because database not consistent with descriptions
    df['AccountNum'] = df.Account.str.extract('(^\d+a|^\d+)')
    df['AccountNum'] = pd.to_numeric(df['AccountNum'])
    ## type(df.iloc[0]['AccountNum'])

    ## create column indicating whether account is income (In) or expense (Out)
    df['InOrOut'] = np.where(df['AccountNum'] < 5000, 'In', 'Out')
    df['AccountNum'] = df['AccountNum'].apply(str) # convert back to string for merge later
    #for i in range(1,len(col_budget)):
    #    df.iloc[:,i] = np.where(df['InOrOut'] == 'In', df.iloc[:,i], -df.iloc[:,i])
    df['Budget'] = np.where(df['InOrOut'] == 'In', df['Budget'], -df['Budget'])

    ## add year and Description columns
    df['Year'] = year
    #today = dt.today().strftime('%Y:%m:%d')
    #df['Description'] = 'Budget ' + str(year) + ' (' + today + ')'
    df['Description'] = budget_header

    ## add file name column
    df['File'] = file

    ## move InOrOut and AccountNum to front of dataframe
    df = df[col_out]

    return df