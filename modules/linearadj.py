import pandas as pd
import numpy as np
import datetime as dt
import regex as re
from modules.date_eom import date_eom
from modules.dateeom import dateeom

def linearadj(filename, dfin, start, end):
    '''
    Read filename to...
    '''

    # %%
    df = dfin.copy()

    ## monthly sum for df and dfc then flatten
    df = dateeom(df)
    #df = df.pivot_table(index=['AccountNum', 'Date'], values=['Amount'], aggfunc=np.sum) # monthly sum
    df = df.pivot_table(index=['AccountNum', 'Date'], values=['Amount'], aggfunc='sum') # monthly sum
    df = df.reset_index()    # flatten

    # %%
    ## read budget_linear.xlsx
    linear = pd.read_excel(filename)
    linear.AccountNum = linear.AccountNum.astype(str)
    linear_list = list(linear.AccountNum.unique())

    ## determine correct columns from linear for budgetb and budgetc and redefine linear dataframe
    currentyear = 'budget'+str(start.year)
    print('currentyear=', currentyear)
    print('str(linear.columns)=', str(linear.columns))
    cols_as_string = ''.join(str(x) for x in linear.columns.tolist())
    if re.search(currentyear, cols_as_string):
        # current year is in the linear adjustment file
        budget = linear[currentyear]
        linear = pd.DataFrame({'AccountNum' : linear.AccountNum, 
                               'budget'     : budget})
    else:
        # still need to add linear adjustment column for current year to file
        print('#################################################################')
        print('# FATAL ERROR: NEED TO ADD COLUMN FOR CURRENT YEAR TO', filename)
        print('#################################################################')
        exit()

    # %%
    ## expand linear to have an entry for each AccountNum for each month
    dicts = []
    for AccountNum in linear_list:
        ## values[0] is needed in the following to extract the value from a series
        amount_lin = linear.loc[linear.AccountNum == AccountNum, 'budget'].values[0] / 12
        dfacct = df.loc[df.AccountNum == AccountNum].copy()
        for month in range(1,13):
            if month > end.month:
                break           # exit for loop
            eom = date_eom(start.year, month)
            dfmonth = dfacct.loc[(dfacct.Date >= dt.date(start.year, month, 1)) & (dfacct.Date <= eom)].copy()
            ## month amount (set to 0 if failes to find anything in them month)
            try:      # error catch
                amount_month = dfmonth.loc[dfmonth.AccountNum == AccountNum, 'Amount'].values[0]
            except:   # error catch
                amount_month = 0
            ## adjustment is differece between linearized plan and actual
            adjustment = amount_lin - amount_month
            dicts.append(
                {
                    'Date': eom,
                    'Account': AccountNum + 'a linear adjustment',
                    'Amount': adjustment,
                    'AccountNum': AccountNum + 'a'
                }
            )
    linear2 = pd.DataFrame(dicts)

    # %%
    ## combine, sort, and renumber
    dfout = pd.concat([dfin, linear2], axis=0)  # rbind
    dfout = dfout.sort_values(by = ['AccountNum', 'Date'], ascending=True, na_position='last')  # sort
    dfout.index = range(len(dfout))              # renumber dataframe

    return dfout, linear2