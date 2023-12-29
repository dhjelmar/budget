#%%
# create dataframe
import pandas as pd
from pprint import pprint

data = {
  'AccountNum': [420, 380, 390, 500, 600, 700],
  'Account': ['first', 'second', 'third', 'fourth', 'fifth', 'sixth'],
  'Value': [50, 40, 55, 56, 57, 60]
}

#load data into a DataFrame object:
df = pd.DataFrame(data)
print('dataframe of accounts')
print(df)

#################################################################################
# %%
## put everything into the dictionary and acccess dictionary entries directly
account_num_dict = {}
for i in range(len(df)):
    account_num_dict[df.iloc[i].AccountNum] = {'Account'   : df.iloc[i].Account, 
                                               'Value'     : df.iloc[i].Value}

## print dictionary
print('print dictionary')
print(account_num_dict, '\n')

## pretty print dictionary
print('pretty print dictionary')
pprint(account_num_dict)
print()

print('use AccountNum key to select object and access Value (should be 40)')
print(account_num_dict[380]['Value'], '\n')


# %%
############################################################
## 