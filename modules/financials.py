#%%
import pandas as pd
import numpy as np
import datetime as dt
import modules as my

class financials():
    '''
    
    '''
    def __init__(self, year, actual, budget):
        self.year = year

        # restrict budget to requested year
        self.budget = budget.loc[budget.Year == year].copy()

        # restrict actual to requested year
        self.actual = actual.loc[actual.Year == year].copy()
                
        # summarize at InOrOut
        self.InOrOut = self.pivot(levels=['InOrOut'])

        # summarize at L1
        self.L1 = self.pivot(levels=['InOrOut', 'L1'])

        # summarize at L2
        self.L2 = self.pivot(levels=['InOrOut', 'L1', 'L2'])

        # summarize at Account level
        self.Account = self.pivot(levels=['InOrOut', 'L1', 'L2', 'Account'])

        # add missing budget entries at time 0
        self.actual = self.add_missing()
                
    def pivot(self, levels):
        actual_sum = self.actual.pivot_table(index=levels, 
                                values=['Amount'], 
                                aggfunc='sum').reset_index()
        if 'Date' in levels: 
            record = actual_sum
        else:
            # 'Date' is not in budget, so skip the merge
            budget_sum = self.budget.pivot_table(index=levels, 
                                            values=['Budget'], 
                                            aggfunc='sum').reset_index()
            record = pd.merge(actual_sum, budget_sum, how='outer', on=levels)
        return record
    
    def history(self, level):
        if level == 'L1':
            df = self.pivot(levels=['Date', 'L1', 'InOrOut'])
        elif level == 'L2':
            df = self.pivot(levels=['Date', 'L2', 'L1', 'InOrOut'])
        elif level == 'Account':
            df = self.pivot(levels=['Date', 'Account', 'L2', 'L1', 'InOrOut'])
        else:
            df = 'invalid level provided to function'
        return df

    def add_missing(self):
        # extract budget items
        time0 = self.budget[['Account', 'Account_budget', 'Budget', 'AccountNum']].copy()
        time0.columns     = ['Account', 'Account_Icon'  , 'Amount', 'AccountNum']
        time0.Amount = 0

        # add to actual
        time0['Date'] = dt.date(self.year, 1, 1)
        time0 = time0[[  'Date', 'Account', 'Account_Icon', 'Amount', 'AccountNum']]
        actual = self.actual[['Date', 'Account', 'Account_Icon', 'Amount', 'AccountNum']].copy()
        actual = pd.concat([time0, actual], axis=0)  # rbind; this changed type from Timestamp to datetime.date
        actual.index = range(len(actual))                 # renumber dataframe

        # concat messed up date format so following fixes it back to datetime.date
        actual['Date'] = pd.to_datetime(actual['Date']).dt.date

        return actual
