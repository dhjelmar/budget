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


# %%
## input phonenumber, username, and password to access api
url = 'https://secure3.iconcmo.com/api/'
phonenumber = "5183772201"
if ('username' not in locals()) | ('password' not in locals()):
    username = input("Input user name:")
    password = input("Input password:")

def erase(var_to_erase):
    strlen = len(var_to_erase)
    offset = sys.getsizeof(var_to_erase) - strlen - 1
    ctypes.memset(id(var_to_erase) + offset, 0, strlen)
    del var_to_erase               # derefrencing the pointer.

eraseit = True
if eraseit == True:
    erase(username)
    erase(password)

# %%
## issue request through api
module = "GL"
section = "Accounts"

query = {"Auth": {"Phone": phonenumber, "Username": username, "Password": password},
         "Request": {"Module": module, "Section": section}}

# turn the query into JSON format
query = json.dumps(query)

# Send the request
r = requests.get(url, data=query, headers={'Content-Type': 'application/json'})

print(r.status_code)
print(r.headers)
print(r.content)


# %%
data = r.json()

# print the mail_to line of the 0th returned data element
print(data['statistics'])
print(data['accounts'][0])

# %%

print(data.keys())              # one of the keys is 'accounts'
accounts = data['accounts']
df = pd.DataFrame.from_dict(accounts)

# %%
