def icon(start, end, startc, endc):
    # %% [markdown]
    # ## Query ICONCMO for Account Data
    # https://secure1.iconcmo.com/developer/

    # %%
    ## standard packages
    import pandas as pd
    import requests       # needed for call to API
    import json
    import csv
    import datetime
    ## for erase function
    import sys 
    import ctypes


    #startc = '2022-01-01'
    #endc   = '2022-12-31'
    #start = '2023-01-01'
    #end   = '2023-12-31'

    start  = str(start)
    end    = str(end)
    startc = str(startc)
    endc   = str(endc)


    username = ""
    password = ""

    # %%
    ## input phonenumber, username, and password to access api
    url = 'https://secure3.iconcmo.com/api/'
    phonenumber = "5183772201"
    ## if ('username' not in locals()) | ('password' not in locals()):
    if (username == "") | (password == ""):
        username = input("Input ICON user name:")
        password = input("Input ICON password:")

    def erase(var_to_erase):
        strlen = len(var_to_erase)
        offset = sys.getsizeof(var_to_erase) - strlen - 1
        ctypes.memset(id(var_to_erase) + offset, 0, strlen)
        del var_to_erase               # derefrencing the pointer.


    # %%
    ## issue request through api

    ## query function
    def query(phonenumber, username, password, module, section,
            start="", end=str(datetime.date.today())):

        if start == "":
            query = {"Auth": {"Phone": phonenumber,
                            "Username": username,
                            "Password": password},
                    "Request": {"Module": module,
                                "Section": section}}
        else:
            query = {"Auth": {"Phone": phonenumber,
                            "Username": username,
                            "Password": password},
                    "Request": {"Module": module,
                                "Section": section,
                                "Filters": {"begin_date": start,
                                            "end_date": end}}}
            

        # turn the query into JSON format
        query = json.dumps(query)

        # Send the request
        r = requests.get(url, data=query, headers={'Content-Type': 'application/json'})

        # secure erase query
        erase(query)
        
        # convert to json
        data = r.json()
        
        return data, r


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

    ## write r to file
    with open('budget_raccount.txt','w') as fd:
        fd.write(raccount.text)



    # %%
    ## submit query to api for comparison year
    d1, r1 = query(phonenumber, username, password, "GL", "Register", startc, endc)
    register1 = d1['register']


    # %%
    ## submit query to api for budget year
    d2, r2 = query(phonenumber, username, password, "GL", "Register", start, end)
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


    # %%
    ## erase username and password
    eraseit = True
    if eraseit == True:
        erase(username)
        erase(password)
        ## erase(raccount)
        ## erase(r1)
        ## erase(r2)

    return df1, df2