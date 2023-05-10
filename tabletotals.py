
def tabletotals(table):
    '''
    Input: Dataframe table with columns: 
        ['InOrOut', 'Category', 'Account', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'SourceOfFunds', 'AccountNum', 'flag']
    
    Output: Dataframe with subtotals and grand total for each 'InOrOut', 'Category', and 'Account'.
    '''
    import pandas as pd
    from highlight import highlight
    ## rename 1st 3 columns from 'InOrOut', 'Category', 'Account' to 'a', 'b', 'c'
    temp = table.copy()
    temp.columns = ['a', 'b', 'c', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'SourceOfFunds', 'AccountNum', 'flag']
    desc = temp.loc[:, ['a', 'b', 'c', 'SourceOfFunds', 'AccountNum', 'flag']]
    nums = temp.loc[:, ['a', 'b', 'c', 'Budget', 'YTD', 'Last YTD', 'Current Month']]

    ## create multiindex for nums with subtotals then flatten again
    ## the following was copied from online where 'a', 'b', and 'c' were the index columns
    ## not sure how to generalize for other options, so I stuck with using a, b and c
    totals = pd.concat([
        nums.assign(
            **{x: '_Total' for x in 'abc'[i:]}
        ).groupby(list('abc')).sum() for i in range(4)
    ]).sort_index()
    totals = totals.reset_index()

    ## combine desc and totals then rename a, b, c
    table_totals = pd.merge(desc, totals, how='right', on=['a', 'b', 'c'])

    table_totals.columns = ['InOrOut', 'Category', 'Account', 'SourceOfFunds', 'AccountNum', 'flag', 'Budget', 'YTD', 'Last YTD', 'Current Month']

    ## move flag to end and drop AccountNum
    table_totals = table_totals[['InOrOut', 'Category', 'Account', 'SourceOfFunds', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'flag']]

    ## first highlight various parts
    ## add a flag for changes to category
    i = table_totals.reset_index().Category                     # first grab index "Category"
    table_totals['flag'] = list(i.ne(i.shift()).cumsum() % 2)   # add flag=1 when "Category" changes
    table_totals.style.apply(highlight, axis=1)                # highlight rows

    ## table_totals = table_totals.set_index(['InOrOut', 'Category'])  # create multiindex
    ## print(table_totals.loc[('Expense', 'Adult Ed')])                # print one index combination
    ## table_totals = table_totals.reset_index()                       # re-flatten multiindex

    ## create printable versions of tables by coverting num dollars to strings with $ signs: table_totals_print
    '''
    table_totals_print = table_totals.copy()
    table_totals_print['Budget']   = table_totals_print['Budget'].apply(dollars.to_str)
    table_totals_print['Last YTD'] = table_totals_print['Last YTD'].apply(dollars.to_str)
    table_totals_print['YTD']      = table_totals_print['YTD'].apply(dollars.to_str)
    table_totals_print['Current Month'] = table_totals_print['Current Month'].apply(dollars.to_str)
    print(table_totals_print)
    '''

    return table_totals