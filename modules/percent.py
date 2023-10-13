# %%
def percent(x, decimals=0):
    '''
    converts a number to a percentage but as a string
    '''
    # simple example to format single number with no decimals as percent
    #    return "{:.0%}".format(x)

    # more complex inserts value of decimals for {}
    if (type(x) == int or type(x) == float):
        return "{:.{}%}".format(x, decimals)
    else:
        return x

# print(percent(1.1, 3))
# print(percent('NA'))

# %%
