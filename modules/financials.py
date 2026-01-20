#%%
import pandas as pd
import numpy as np
import modules as my

class financials():
    '''
    
    '''
    def __init__(self, year, actual, budget, debug=False):
        self.year = year
        self.actual = actual.loc[actual.Year == year].copy()
        self.budget = budget.loc[budget.Year == year].copy()

        # summarize at InOrOut
        self.InOrOut = self.pivot(self.actual, self.budget, levels=['InOrOut'])

        # summarize at L1
        self.L1 = self.pivot(self.actual, self.budget, levels=['InOrOut', 'L1'])

        # set levels for pivot table and plots
        self.L2 = self.pivot(self.actual, self.budget, levels=['InOrOut', 'L1', 'L2'])

    def pivot(self, actual, budget, levels):
        actual_sum = actual.pivot_table(index=levels, 
                                values=['Amount'], 
                                aggfunc='sum').reset_index()
        budget_sum = budget.pivot_table(index=levels, 
                                        values=['Budget'], 
                                        aggfunc='sum').reset_index()
        record = pd.merge(actual_sum, budget_sum, how='outer', on=levels)
        return record

