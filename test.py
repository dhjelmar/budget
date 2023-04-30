# %%
from erase import erase
a = 'asdfg'
print('before erase: a = ', a)

# %%
erase(a)
print('after erase: a = ', a)

# %%
a
# %%
from random import randint
import pandas as pd

x = [randint(0, 1) for p in range(0, 10)]

sample_dict = {"Col1": [randint(0, 1) for p in range(0, 10)],
               "Col2": [randint(0, 1) for p in range(0, 10)],
               "Col3": [randint(0, 1) for p in range(0, 10)],
               "Col4": [randint(0, 1) for p in range(0, 10)],
               "Col5": [randint(0, 1) for p in range(0, 10)],
               "Col6": [randint(0, 1) for p in range(0, 10)]}

sample = pd.DataFrame(sample_dict)
# %%
sample
# %%
sample.style.apply(lambda x: ["background: orange" if v != x.iloc[0] else "" for v in x], axis = 1)

# %%
from random import randint
import pandas as pd

x = [randint(0, 1) for p in range(0, 10)]

sample_dict = {"Col1": [randint(0, 1) for p in range(0, 10)],
               "Col2": [randint(0, 1) for p in range(0, 10)],
               "Col3": [randint(0, 1) for p in range(0, 10)],
               "Col4": [randint(0, 1) for p in range(0, 10)],
               "Col5": [randint(0, 1) for p in range(0, 10)],
               "Col6": [randint(0, 1) for p in range(0, 10)]}

sample = pd.DataFrame(sample_dict)

sample = sample.style.apply(lambda x: ["background-color: orange" if v != x.iloc[0] else "background_color: none" for v in x], axis=1)
sample.to_excel('sample.xlsx', engine='openpyxl')


# %%
# importing pandas as pd 
import pandas as pd 
  
# creating the dataframe
df = pd.DataFrame({"A" : [14, 4, 5, 4, 1],
                   "B" : [5, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "D" : [14, 3, 6, 2, 6],
                   "E" : [23, 45, 64, 32, 23]}) 
  
print("Original DataFrame :")
display(df)
  
# function definition
def highlight_cols(x):
      
    # copy df to new dataframe
    df = x.copy()
      
    # set all values to white color
    df.loc[:, :] = 'background-color: white'         # this works
      
    # overwrite values in 3 columns to grey color
    df[['B', 'C', 'E']] = 'background-color: grey'   # this works

    # overwrite values in rows where C is 7
    df.loc[df['C'] == 7] = 'background-color: red'   # this does not work
    df.loc[df['C'] == 7] = 'font-weight: bold'       # this does not work
    
    # return color df
    return df 
  
print("Highlighted DataFrame :")
display(df.style.apply(highlight_cols, axis = None))

# %%


# %%
# importing pandas as pd 
import pandas as pd 
  
# creating the dataframe
df = pd.DataFrame({"A" : [14, 4, 5, 4, 1],
                   "B" : [5, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "D" : [14, 3, 6, 2, 6],
                   "E" : [23, 45, 64, 32, 23]}) 
  
print("Original DataFrame :")
display(df)
  
# function definition
def highlight_cols(x):
      
    # copy df to new dataframe
    df = x.copy()
      
    # set all values to white color
    df.loc[:, :] = 'background-color: white'         # this works
      
    ## overwrite values in 3 columns to grey color
    #df[['B', 'C', 'E']] = 'background-color: grey'   # this works

    # overwrite values in rows where C is 7
    df.loc[df['C'] == 7] = 'background-color: red'   # this does not work
    #df.loc[df['C'] == 7] = 'font-weight: bold'       # this does not work
    
    # return color df
    return df 
  
print("Highlighted DataFrame :")
display(df.style.apply(highlight_cols, axis = None))
# %%

import pandas as pd
import numpy as np

np.random.seed(24)
df = pd.DataFrame({'A': np.linspace(1, 10, 10)})

df = pd.concat([df, pd.DataFrame(np.random.randn(10, 4), columns=list('BCDE'))],
               axis=1)
df.iloc[0, 2] = np.nan

def highlight_greaterthan(s, threshold, column):
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = s.loc[column] >= threshold
    return ['background-color: yellow' if is_max.any() else '' for v in is_max]


df.style.apply(highlight_greaterthan, threshold=1.0, column=['C', 'B'], axis=1)



# %%
import pandas as pd

df = pd.DataFrame({"A" : [14, 4, 5, 4, 1],
                   "B" : [5, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "D" : [14, 3, 6, 2, 6],
                   "E" : [23, 45, 64, 32, 23]}) 

def highlight(x):
    df = x.copy()
    df.loc[df['C'] == 7] = 'background-color: red'
    df.loc[df['C'] == 7] = 'font-weight: bold'
    return df

df.style.apply(highlight, axis=1)


# %%
import pandas as pd
df = pd.DataFrame({"A" : [14, 4, 5, 4, 1],
                   "B" : [5, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "D" : [14, 3, 6, 2, 6],
                   "E" : [23, 45, 64, 32, 23]}) 
def highlight(s):
    if s.C == 7:
        return ['background-color: yellow'] * len(s)
    else:
        return ['background-color: white'] * len(s)
df.style.apply(highlight, axis=1)

# %%
import pandas as pd
df = pd.DataFrame({"A" : [14, 4, 5, 4, 1],
                   "B" : [5, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "D" : [14, 3, 6, 2, 6],
                   "E" : [23, 45, 64, 32, 23]}) 
def highlight(s):
    if s.C == 7:
        # return ['background-color: yellow'] * len(s)
        # return ['font-weight: bold'] * len(s)
        # return [{'background-color: yellow' & 'font-weight: bold'}] * len(s)
        # return [('background-color: yellow') & ('font-weight: bold')] * len(s)
        return [{('background-color: yellow') & ('font-weight: bold')}] * len(s)
    else:
        return ['background-color: white'] * len(s)
df.style.apply(highlight, axis=1)

# %%

https://stackoverflow.com/questions/76088335/pandas-style-function-to-set-multiple-row-attributes-for-matches-to-column-value


Pandas style function to set multiple row attributes for matches to column value



For rows in a pandas dataframe that have a given value in a given column, I cannot figure out how to make those rows both colored yellow and bold type.



The following coding successfully colors a row based on a column value. Or it can be used to successfully bold type a row based on a column value. The following is based on
[this link by Stephen](https://stackoverflow.com/a/48306463/16658771).

```
import pandas as pd

df = pd.DataFrame({"A" : [14, 4, 5, 4, 1],
                   "B" : [5, 2, 54, 3, 2],
                   "C" : [20, 20, 7, 3, 8], 
                   "D" : [14, 3, 6, 2, 6],
                   "E" : [23, 45, 64, 32, 23]}) 

def highlight(s):
    if s.C == 7:
        return ['background-color: yellow'] * len(s)                             # this works
        # return ['font-weight: bold'] * len(s)                                    # this works
        # return [{'background-color: yellow' & 'font-weight: bold'}] * len(s)     # this fails
        # return [('background-color: yellow') & ('font-weight: bold')] * len(s)   # this fails
        # return [{('background-color: yellow') & ('font-weight: bold')}] * len(s) # this fails
    else:
        return ['background-color: white'] * len(s)

df.style.apply(highlight, axis=1)
```

[Hopefully this is an image of the output](https://i.stack.imgur.com/3uon9.png).

I cannot figure out how to make the row where df.C == 7 both colored and bold.