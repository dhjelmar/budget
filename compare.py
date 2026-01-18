#%%
import pandas as pd
import numpy as np
from datetime import datetime as dt
from modules.read_map import read_map
from modules.mapit import mapit
from modules.convert import convert
import jellyfish  # approximate match

#%%
### read prior year or attempt budget info saved in budget_all.xlsx
#df = pd.read_excel('input_files/budget_all.xlsx')
#df = df.drop('Account (map)', axis=1)
#df = df.drop('Match Level', axis=1)

#%%
## Add new budget file to info saved in budget_all.xlsx

'''
## use following to create list of several files to read
file = []
file.append('budget_2024_2023_12_asking_fixed.xlsx')
file.append('budget_2024_2024_01_13_dave.xlsx')

## overwrite the above with the following to only work with one file
file = 'budget_2024_2024_01_13_dave.xlsx'
file = 'budget_2025.xlsx'

# read each office formatted budget file and combine with df
if type(file) == str:
    budget = convert(file, col_acct=0, col_budget=3)
    df = pd.concat([df, budget], axis=0)
else:
    for i in range(0,len(file), col_budget=3):
        budget = convert(file[i])
        df = pd.concat([df, budget], axis=0)
'''

# read and convert office-formated budget file
file = 'budget_2025.xlsx'
budget = convert(file, col_acct=0, col_budget=1, year=2023)
df = budget
budget = convert(file, col_acct=0, col_budget=2, year=2024)
df = pd.concat([df, budget], axis=0)
budget = convert(file, col_acct=0, col_budget=5, year=2025)
df = pd.concat([df, budget], axis=0)
file = 'budget_2026.xlsx'
budget = convert(file, col_acct=0, col_budget=1, year=2025)
df = pd.concat([df, budget], axis=0)
budget = convert(file, col_acct=0, col_budget=3, year=2026)
df = pd.concat([df, budget], axis=0)


#%% 
## map to categories
#map, map_duplicates = read_map(sheet='2026')
map, map_duplicates = read_map()

#%%
## first need to convert AccountNum to string for merge operation
df['AccountNum'] = df['AccountNum'].apply(str)
dfmapped, missing = mapit(df, map)

#%%
## drop and rename columns from: 
dfmapped = dfmapped.drop('InOrOut_x', axis=1)
dfmapped.rename(columns = {"Account_x": "Account (budget)"}, inplace = True) 
dfmapped = dfmapped.drop('InOrOut_y', axis=1)
dfmapped.rename(columns = {"Account_y": "Account (map)"}, inplace = True) 


#%%
## Check actual for mismatched account names
mismatched_dict = []
for row in range(len(dfmapped)):
    a = jellyfish.jaro_similarity(str(dfmapped.loc[row,'Account (budget)']), str(dfmapped.loc[row,'Account (map)']))    # approximate match
    mismatched_dict.append(a)
dfmapped['Match Level'] = mismatched_dict

#%%
## reorder specific columns but keep all columns
allcols = list(dfmapped)
## first = ['Year', 'Description', 'InOrOut', 'AccountNum', 'Account (budget)', 'Budget', 'Category', 'SourceOfFunds', 'Purpose', 'InternalExternal', 'File']
first = ['Year', 'Description', 'InOrOut', 'AccountNum', 'Account (budget)', 'Account (map)', 'Match Level', 'Budget', 'Category', 'SourceOfFunds', 'File']
first = ['Year', 'Description', 'InOrOut', 'AccountNum', 'Account (budget)', 'Account (map)', 'Match Level', 'Budget', 'File']
rest = [i for i in allcols if i not in first]
dfmapped_new = pd.concat([dfmapped[first],dfmapped[rest]], axis=1)
dfmapped = dfmapped_new

#%%
## write to Excel
dfmapped.to_excel('compare_out.xlsx', index=False)

#%%