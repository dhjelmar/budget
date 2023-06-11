## query function
import datetime as dt
def query(phonenumber, username, password, module, section,
        start="", end=str(dt.date.today())):
    '''
    Function to issue query to IconCMO API

    Output
    ------
    r    = response to the query
    data = response converted to json format

    Example
    -------
        daccount, raccount = query(phonenumber, username, password, "GL", "Accounts")
    '''
    import json
    import requests       # needed for call to API

    ## input phonenumber, username, and password to access api
    url = 'https://secure3.iconcmo.com/api/'

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

    # erase variables
    del(query)
    del(phonenumber)
    del(password)
    
    # convert to json
    data = r.json()
    
    return data, r

