# %%
import sys

def mapit(df, map, fail_if_missing=False):
    '''
    pd.merge(df1, map, how='left', on='AccountNum')
    '''

    import pandas as pd
    import regex as re

    df = pd.merge(df, map, how='left', on='AccountNum')

    ## flag any line items from dataframe that are not in the map (e.g., so no Category assigned)
    nan_values = df[df['L2'].isna()]
    missing_from_map = df[df['AccountNum'].isin(nan_values.AccountNum.to_list())]
    if (fail_if_missing)&(len(nan_values)) != 0:
        print('')
        print('FATAL ERROR: No assignment in map.xlsx file for the following.')
        print('             Fix entry in Icon or, if Icon is correct, add new entry to map.xlsx.')
        print(missing_from_map[0:3])
        input('Press enter to exit this window')
        sys.exit()

        '''
        ## classify anything that does not have Category defined in map
        mask = df['L2'].isna()
        df.loc[mask, 'L1'] = 'Xbudget'
        df.loc[mask, 'L2'] = 'Xbudget'
       
        ## if Account is missing from map, replace it with Account from dataframe
        if 'Account' in df:
            df.loc[df['Account'].isna(), 'Account'] = df['AccountNum']
        if 'Account_x' in df:
            df.loc[df['Account_x'].isna(), 'Account_x'] = df['AccountNum']
        if 'Account_y' in df:
            df.loc[df['Account_y'].isna(), 'Account_y'] = df['AccountNum']

        ## sum dollar fields
        dollarfields = [x for x in df.columns if re.findall(r'Amount',x)]
        df['dollarsum'] = 0   # initialize new variable
        for i in dollarfields:
            df.loc[mask, 'dollarsum'] = df.loc[mask, 'dollarsum'] + df.loc[mask, i]

        ## if not defined, set InOrOut based on dollar fields being positive or negative
        df.loc[(df.InOrOut.isna()) & (df.dollarsum >= 0), 'InOrOut'] = 'In' 
        df.loc[(df.InOrOut.isna()) & (df.dollarsum <  0), 'InOrOut'] = 'Out' 
        df.loc[(df.Category == 'Xbudget'), 'InOrOut'] = 'Xbudget' 
        '''

    return df, missing_from_map


#import pandas as pd
#df = pd.DataFrame({"A" : [14, 4, 5, 4, 1],
#                   "AccountNum" : ['100', '200', '300', '400', '500'],
#                   "Amount" : [1,2,-3,-4,-5],
#                   "Amounta" : [2,3,-1,-1,-1]})
#map = pd.DataFrame({"InOrOut" : ['In', 'Out'],
#                    "Category" : ['asdf', 'jkl;'],
#                    "SourceOfFunds" : ['end', 'cov'],
#                    "Account" : ['200 some income', '300 some expense'],
#                    "AccountNum" : ['200', '300'] })
#out, junk = mapit(df,map)
#out

# %%
