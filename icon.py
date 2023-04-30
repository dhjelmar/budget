def icon(startb, endb, startc, endc):
    '''
    Import following from IconCMO: Accounts
                                   Register entries between startb and endb
                                   Register entries between startc and endc

    Input
        dates in string (e.g., '2023-01-01') or datetime.date format (e.g., datetime.date(2023,1,1))
                                   
    Output
        df1 = Register entries between startc and endc with Accounts identified
        df2 = Register entries between startb and endb with Accounts identified


    Example
        actualb_read, actualc_read = icon.icon(startb, endb, startc, endc)

    '''

    # %% [markdown]
    # ## Query ICONCMO for Account Data
    # https://secure1.iconcmo.com/developer/

    # %%
    ## standard packages
    import pandas as pd
    import csv
    ## my functions
    import dollars
    from query import query

    #startc = '2022-01-01'
    #endc   = '2022-12-31'
    #startb = '2023-01-01'
    #endb   = '2023-12-31'

    startb  = str(startb)
    endb    = str(endb)
    startc = str(startc)
    endc   = str(endc)


    username = ""
    password = ""

    # %%
    phonenumber = "5183772201"
    ## if ('username' not in locals()) | ('password' not in locals()):
    if (username == "") | (password == ""):
        username = input("Input ICON user name:")
        password = input("Input ICON password:")

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
    ## submit query to api for comparison year
    d1, r1 = query(phonenumber, username, password, "GL", "Register", startc, endc)
    register1 = d1['register']


    # %%
    ## submit query to api for budget year
    d2, r2 = query(phonenumber, username, password, "GL", "Register", startb, endb)
    register2 = d2['register']




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
    ## create dataframe from 'register1', using 'account_map' to get the account type
    ## create an empty list, fill it, then convert to dataframe
    list1 = []
    for transaction in register1:
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
    df1 = pd.DataFrame(list1)
    df1.columns = ['Date', 'Account Type', 'Account', 'Amount']




    # %%
    ## create dataframe from 'register2', using 'account_map' to get the account type
    ## create an empty list, fill it, then convert to dataframe
    list2 = []
    for transaction in register2:
        for line_item in transaction['line_items']:
            account_type = account_map[line_item['account_id']]
            if account_type == "Expenditures" or account_type == "Revenues":
                amount = line_item['credit']
                if amount == "$0.00":
                    amount = "-" + line_item['debit']
                account_name_arr = line_item['account_name'].split(':')
                account_name = account_name_arr[len(account_name_arr) - 1]
                list2.append([transaction['date'], account_type, account_name, amount])
    ## convert to dataframe
    df2 = pd.DataFrame(list2)
    df2.columns = ['Date', 'Account Type', 'Account', 'Amount']

    ## drop 'Account Type' column (i.e., whether "Revenues" or "Expenditures")
    df1 = df1.drop(columns=['Account Type'])
    df2 = df2.drop(columns=['Account Type'])

    ## add AccountNum column
    df1['Account'] = df1['Account'].str.strip()    # strip leading and trailing white space
    ## create another column with budget line item number only because database not consistent with descriptions
    df1['AccountNum'] = df1.Account.str.extract('(\d+)')
    df2['Account'] = df2['Account'].str.strip()    # strip leading and trailing white space
    ## create another column with budget line item number only because database not consistent with descriptions
    df2['AccountNum'] = df2.Account.str.extract('(\d+)')

    ## convert Ammount from string to number
    df1['Amount'] = df1['Amount'].apply(dollars.to_num)
    df2['Amount'] = df2['Amount'].apply(dollars.to_num)

    # %%
    ## erase username and password
    eraseit = True
    if eraseit == True:
        del(username)
        del(password)
        ## del(raccount)
        ## del(r1)
        ## del(r2)

    return df2, df1