def highlight(df):
    '''
    highlight rows of dataframe that have 1 in column "flag"
    highlight and bold rows of a dataframe that have "_Total" in column "Account"

    Input:
    ------
    df = pandas dataframe with column "flag" with 0 and 1 values
         and "Account" column which can contain "_Total" values

    Example:
    df.style.apply(highlight, axis=1)
    '''
 
    if df.flag == 1:
        if df.Account == "_Total":
            return ['color: black; background-color: lightgrey; font-weight: bold'] * len(df)
        else:
            return ['color: black; background-color: lightgrey'] * len(df)
            
    else:
        if df.Account == "_Total":
            return ['color: black; background-color: white; font-weight: bold'] * len(df)
        else:
            return ['color: black; background-color: white'] * len(df)
    
    
'''
## Example
import pandas as pd

df = pd.DataFrame({"A" : [14.33, 4.33, 5.44, 4.45, 1.99],
                   "B" : [5, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "names" : ['FRED', 'Dave', 'joe', 'Tom', 'asdf'],
                   "Account" : ['one', 'two', 'three', '_Total', 'five'],
                   "flag" : [1, 0, 1, 1, 0]}) 

print('Before highlight')
print(df)

print('')
print('After highlight')
df.style.apply(highlight, axis=1)
'''