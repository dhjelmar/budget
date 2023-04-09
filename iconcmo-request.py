# %% [markdown]
# ## Query ICONCMO for Account Data
# https://secure1.iconcmo.com/developer/

# %%
## standard packages
import pandas as pd     # needed to install package
## import packages
import requests         # needed to install package
import json
## for erase function
import sys 
import ctypes

username = ""
password = ""

# %%
## input phonenumber, username, and password to access api
url = 'https://secure3.iconcmo.com/api/'
phonenumber = "5183772201"
## if ('username' not in locals()) | ('password' not in locals()):
if (username == "") | (password == ""):
    username = input("Input user name:")
    password = input("Input password:")

def erase(var_to_erase):
    strlen = len(var_to_erase)
    offset = sys.getsizeof(var_to_erase) - strlen - 1
    ctypes.memset(id(var_to_erase) + offset, 0, strlen)
    del var_to_erase               # derefrencing the pointer.


# %%
## issue request through api

## query function
def query(phonenumber, username, password, module, section):
    query = {"Auth": {"Phone": phonenumber, "Username": username, "Password": password}
            ,"Request": {"Module": module, "Section": section}}

    # turn the query into JSON format
    out = json.dumps(query)

    # Send the request
    r = requests.get(url, data=out, headers={'Content-Type': 'application/json'})

    # convert to json
    data = r.json()
    
    return data, r


# %%
## submit 1st query to api
data1, r1 = query(phonenumber, username, password, "GL", "Accounts")
print(r1.status_code)
print(r1.headers)
print(r1.content)

## write r1 to file
with open('budget_r1.txt','w') as fd:
    fd.write(r1.text)


# %%
## submit 2nd query to api

data2, r2 = query(phonenumber, username, password, "GL", "Register")
print(r2.status_code)
print(r2.headers)
print(r2.content)

## write r2 to file
with open('budget_r2.txt','w') as fd:
    fd.write(r2.text)


# %%
## erase username and password
eraseit = True
if eraseit == True:
    erase(username)
    erase(password)


# %%
# print the mail_to line of the 0th returned data element
print(data1['statistics'])
print(data1['accounts'][0])

# %%

print(data1.keys())              # one of the keys is 'accounts'
accounts = data1['accounts']
df = pd.DataFrame.from_dict(accounts)

# %%
