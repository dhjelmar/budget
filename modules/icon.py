from getpass4 import getpass
import pandas as pd
import modules.dollars as dollars
from modules.query import query

def icon(start, end, interactive):
    '''
    Import following from IconCMO: Accounts
                                   Register entries between start and end

    Input
        dates in string (e.g., '2023-01-01') or datetime.date format (e.g., datetime.date(2023,1,1))
                                   
    Output
        df = Register entries between start and end with Accounts identified

    Example
        actual = my.icon(start, end)

    '''

    # %% [markdown]
    # ## Query ICONCMO for Account Data
    # https://secure1.iconcmo.com/developer/

    # %%
    #start = '2022-01-01'
    #end   = '2022-12-31'

    start  = str(start)
    end    = str(end)

    username = ""
    password = ""

    # %%
    phonenumber = "5183772201"
    ## if ('username' not in locals()) | ('password' not in locals()):
    if (username == "") | (password == ""):
        print()
        username = input("Enter ICON user name:")
        if interactive:
            password = input("Enter ICON password:")
        else:
            password = getpass(prompt='Enter ICON password: ')

    # %%
    ## issue request through api

    ##-----------------------------------------------------------------------------
    # %%
    ## submit 1st query to api
    daccount, raccount = query(phonenumber, username, password, "GL", "Accounts")
    #print(raccount.status_code)
    #print(raccount.headers)
    #print(raccount.content)

    ## show parts of daccount
    daccount.keys()
    ## assign accounts key to variable accounts
    accounts = daccount['accounts']

    ## # print the mail_to line of the 0th returned daccount element
    ## print(daccount['statistics'])
    ## print(daccount['accounts'][0])
    ## 
    ## print(daccount.keys())              # one of the keys is 'accounts'
    ## accounts = daccount['accounts']
    ## df = pd.DataFrame.from_dict(accounts)

    ## ## write r to file
    ## with open('budget_raccount.txt','w') as fd:
    ##     fd.write(raccount.text)

    # %%
    ## submit query to api for requested date range
    d1, r1 = query(phonenumber, username, password, "GL", "Register", start, end)
    register = d1['register']

    ##-----------------------------------------------------------------------------
    # %% [markdown]
    # # Build Account Map

    #drill down recursively into the accounts and sub-accounts to get a dictionary where each account ID points to the account type
    def build_account_map(accounts):
        for account in accounts:
            account_map[account['id']] = account['account_type_1']
            if account.get('sub-accounts'):
                build_account_map(account['sub-accounts'])

    account_map = {}
    build_account_map(accounts)

    # %%
    ##create spreadsheet from 'register', using 'account_map' to get the account type
    #with open("revenues-and-expenses.csv", "w", newline='') as file:
    #    writer = csv.writer(file)
    #    writer.writerow(["date", "account type", "account", "amount"])
    #    for transaction in register:
    #        for line_item in transaction['line_items']:
    #            account_type = account_map[line_item['account_id']]
    #            if account_type == "Expenditures" or account_type == "Revenues":
    #                amount = line_item['credit']
    #                if amount == "$0.00":
    #                    amount = "-" + line_item['debit']
    #                account_name_arr = line_item['account_name'].split(':')
    #                account_name = account_name_arr[len(account_name_arr) - 1]
    #                writer.writerow([transaction['date'], account_type, account_name, amount])


    # %%
    ## create dataframe from 'register', using 'account_map' to get the account type
    ## create an empty list, fill it, then convert to dataframe
    list1 = []
    for transaction in register:
        for line_item in transaction['line_items']:
            account_type = account_map[line_item['account_id']]
            if account_type == "Expenditures" or account_type == "Revenues":
                amount = line_item['credit']
                if amount == "$0.00":
                    amount = "-" + line_item['debit']
                account_name_arr = line_item['account_name'].split(':')
                account_name = account_name_arr[len(account_name_arr) - 1]
                list1.append([transaction['date'], account_type, account_name, amount])
    ## convert to dataframe
    df = pd.DataFrame(list1)
    df.columns = ['Date', 'Account Type', 'Account', 'Amount']

    ## convert dates from str to datetime to date
    df.Date = pd.to_datetime(df.Date).dt.date 
    
    ## drop 'Account Type' column (i.e., whether "Revenues" or "Expenditures")
    df = df.drop(columns=['Account Type'])

    ## add AccountNum column
    df['Account'] = df['Account'].str.strip()    # strip leading and trailing white space

    ## convert Ammount from string to number
    df['Amount'] = df['Amount'].apply(dollars.to_num)

    ## strip leading and trailing white space
    df['Account'] = df['Account'].str.strip()

    # manually correct known errors in Icon
    mask = df.Account == '6000 Worship & Arts ⟩  Worship & Arts Senior Pastor ⟩ 5011 Business & Auto Expense Sr. Pastor'
    df.loc[mask,'Account'] = '5017 Business & Auto Sr. Pastor'

    ## extract account numbers to separate variable
    #df['AccountNum'] = df.Account.str.extract('(\d+)')
    df['AccountNum'] = df['Account'].str[:4]
    df.AccountNum = df.AccountNum.astype(str)

    # %%
    ## erase username and password
    eraseit = True
    if eraseit == True:
        del(username)
        del(password)
        ## del(raccount)
        ## del(r1)
        ## del(r2)

    return df
