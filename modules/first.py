
#%%
# move some columns to front of dataframe without specifying all columns in dataframe
def first(df, first):
    '''
    df    = dataframe
    first = list of columns to move to front of df
    '''
    new_column_order = first + [col for col in df.columns if col not in first]
    df = df[new_column_order]
    return df

'''
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9],
    'D': [10, 11, 12],
    'E': [13, 14, 15]
})
df = first(df, ['E', 'C'])
df

# delete columns
#df = df.drop(columns=['C','D'])
#df
'''
#%%