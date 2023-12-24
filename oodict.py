#%%
# create dataframe
import pandas as pd

data = {
  'AccountNum': [420, 380, 390],
  'Account': ['first', 'second', 'third'],
  'Value': [50, 40, 45]
}

#load data into a DataFrame object:
df = pd.DataFrame(data)
print('dataframe of accounts')
print(df)

########################################################################
#%%
## create account objects

## define class for account objects
class account_class():
    def __init__(self, AccountNum, Account, Value):
        self.AccountNum = AccountNum
        self.Account = Account
        self.Value = Value

## create account objects
account_obj = [account_class(a.AccountNum, a.Account, a.Value) for a in df.itertuples()]
print('example to access "Account" for account object with index 1')
print(account_obj[1].Account)


########################################################################
#%%
## Instead of above, create account dictionary to more easily access acounts by AccountNum
account_dict = {}
account_list = []
for i in range(len(df)):
    # account_dict[i] = {'index': i,
    #                    'AccountNum': df.iloc[i].AccountNum}
    account_dict[i] = {'AccountNum': df.iloc[i].AccountNum}
    # account_list[i] = account_class(df.iloc[i].AccountNum, 
    #                                 df.iloc[i].Account, 
    #                                 df.iloc[i].Value)
    account_list.append(account_class(df.iloc[i].AccountNum, 
                                      df.iloc[i].Account, 
                                      df.iloc[i].Value))

## print dictionary
print(list(account_dict.values()))


#%%
## access object values
print('access account list object using index for 2nd entry to get Value')
print(account_list[1].Value)

## using dictionary
print('access account list object using AccountNum for 2nd entry to get Value')
print(account_list[1].Account)



# %%
