import dataframe_image as dfi    # had to install with pip
import modules.dollars as dollars

def category_table(inout, category, table, path, fignum):
    df = table.loc[(table.InOrOut == inout) & (table.Category == category),:].copy()
    ## if Account = NaN, then replace it with AccountNum
    df.loc[df['Account'].isnull(), 'Account'] = df['AccountNum']
    df = df.drop(['InOrOut', 'Category', 'AccountNum', 'flag'], axis=1)
    df['Budget'] = df['Budget'].apply(dollars.to_str)
    df['YTD'] = df['YTD'].apply(dollars.to_str)
    df['Last YTD'] = df['Last YTD'].apply(dollars.to_str)
    df['Current Month'] = df['Current Month'].apply(dollars.to_str)
    df = df.reset_index(drop=True)
    rows = len(df)
    filename = "category_{0:01d}".format(fignum)
    if rows > 30:     # 19 seems to be the max for an image but fewer i
        df1 = df.iloc[range(0,15)]
        df2 = df.iloc[range(15,30)]
        df3 = df.iloc[range(30,rows)]
        dfi.export(df1, path+filename+'_table1.png', dpi=300)
        dfi.export(df2, path+filename+'_table2.png', dpi=300)
        dfi.export(df3, path+filename+'_table3.png', dpi=300)
    elif rows > 15:  # 19 seems to be the max for an image but fewer if some need double lines
        df1 = df.iloc[range(0,15)]
        df2 = df.iloc[range(15,rows)]
        dfi.export(df1, path+filename+'_table1.png', dpi=300)
        dfi.export(df2, path+filename+'_table2.png', dpi=300)
    else:
        dfi.export(df, path+filename+'_table.png', dpi=300)

    return df