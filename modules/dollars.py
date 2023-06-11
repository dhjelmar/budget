# %%
def to_str(x, cents=False):
    '''
    converts a number to currency but as a string
    '''
    ## return "${:.1f}K".format(x/1000)
    if cents == False:
        xstr = "${:,.0f}".format(x)
    else:
        xstr = "${:,.2f}".format(x)
    ## return "${:,.0f}".format(x)
    return xstr


# %%
def to_num(x):
    '''
    converts a dollar string to number
    '''
    import regex as re
    #from decimal import Decimal
    #return Decimal(re.sub(r'[^\d\-.]', '', x))
    num = float(re.sub('[$]', '', x))
    return num


# %%
def example():
    import pandas as pd
    import regex as re
    import modules.dollars as dollars
    df = pd.DataFrame({'team': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
                    'points': [18, 22, 19, 14, 14, 11, 20, 28, 30],
                    'assists': [5, 7, 7, 9, 12, 9, 9, 4, 15],
                    'cash': [5, -7, 7, 9, -12, 9, 9, 4, 15]})

    ## pandas dataframe example
    df['cash as str'] = df['cash'].apply(dollars.to_str)
    df['cash w/ cents'] = df['cash'].apply(dollars.to_str, cents=True)
    df['cash as num'] = df['cash as str'].apply(dollars.to_num)
    print(df)

    ## simple example
    print()
    print(dollars.to_str(df.loc[2,'cash']))
    print(dollars.to_num(df.loc[2,'cash as str']))

    ## list example
    print()
    dollarlist = ['$1', '$2', '$3']
    output_list = list(map(dollars.to_num, dollarlist))
    print(output_list)

# %%
