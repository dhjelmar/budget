# %%[markdown]   # Jupyter-like notebook in text file using ipython extension and ipykernel package
# ## Budget Vs. Actual Spending

# + User input for budget Excel file with following columns:
#   + xxxxxx
#   + xxxxxx
#   + xxxxxx
#   + xxxxxx
# + User input for budget year and comparison year
# + Reads budget from Excel
# + Reads actual spending for budget and comparison years from ICONCMO API
# + Creates
#   + Table and figures to compare at high level
#   + Table and figures to compare for line items



# %% 
## import packages
import pandas as pd
import datetime as dt
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import regex as re
import sys
import calendar
import dataframe_image as dfi    # had to install with pip
import jellyfish

## import my functions
from set_dates import set_dates
from read_map import read_map
from read_budget import read_budget
from mapit import mapit
from icon import icon     # gives access to all function icon() in icon.py; e.g., icon(startb, endb, startc, endc)
from linearadj import linearadj
import dollars            # gives access to all fucntions in dollars.py; e.g., dollars.to_num('-$4')
from highlight import highlight
from dupacct import dupacct
from dateeom import dateeom
from tabletotals import tabletotals
from plotit import plotit

os.getcwd()


###############################################################################
# %% [markdown]
## Set budget and comparison year start and end dates
startb, endb, startc, endc = set_dates()


###############################################################################
# %% [markdown]
## READ MAP OF ACCOUNTS TO CATEGORIES INTO DATAFRAME: map
map, map_duplicates = read_map()


###############################################################################
# %% [markdown]
## READ BUDGET DATA INTO DATAFRAME: budget
budget, budget_duplicates = read_budget(startb.year)


## # %% [markdown]
## ## map categories to budget entries
## budget, missing = mapit(budget, map)

 
###############################################################################
# %% [markdown]
## Obtain ICON entries for budget year and comparison year
refresh = False
if refresh == True:
    actualb, actualc = icon(startb, endb, startc, endc)
    actualb.to_csv('actualb.csv', index=False)
    actualc.to_csv('actualc.csv', index=False)
else:
    actualb = pd.read_csv('actualb.csv')
    actualc = pd.read_csv('actualc.csv')
    actualb['Date'] = pd.to_datetime(actualb['Date']).dt.date
    actualc['Date'] = pd.to_datetime(actualc['Date']).dt.date
    actualb['AccountNum'] = actualb['AccountNum'].astype(str)
    actualc['AccountNum'] = actualc['AccountNum'].astype(str)


###############################################################################
# %% [markdown]
## Read investment data file  (NOT CODED YET)


###############################################################################
# %% [markdown]
## CREATE TABLE DATAFRAME FOR OUTPUT: table, table_totals

# %%
## prior month expenses
actualbm = dateeom(actualb.copy())
actualbm = actualbm.loc[actualbm['Date'] == endb]
actualbm

# %%
## for year to date summations, create new dataframes stripping actualc to same duration as actualb
ytdb = actualb.copy()
ytdc = actualc.copy()
ytdc = ytdc.loc[(actualc['Date'] >= startc) & (actualc['Date'] <= (startc + (endb - startb)))]

# %%
## use pivot table to sum ytd and current month totals
## pivot = budget.pivot_table(index=['InOrOut', 'Committee', 'GreenSheet'], values='Budget', aggfunc=np.sum)
ytdb = ytdb.pivot_table(index=['AccountNum', 'Account'], values='Amount', aggfunc=np.sum).reset_index()
ytdb.columns = ['AccountNum', 'Accountb', 'YTD']
ytdc = ytdc.pivot_table(index=['AccountNum', 'Account'], values='Amount', aggfunc=np.sum).reset_index()
ytdc.columns = ['AccountNum', 'Accountc', 'Last YTD']
actualbm = actualbm.pivot_table(index=['AccountNum', 'Account'], values='Amount', aggfunc=np.sum).reset_index()
actualbm.columns = ['AccountNum', 'Accountbm', 'Current Month']


# %%

## full, outer join (i.e., include any line item in any dataframe) for budget, ytdb, and ytdc
temp = budget.loc[:, ['AccountNum', 'Accounta', 'Budget']]
temp = pd.merge(temp, ytdb, how='outer', on='AccountNum')
temp = pd.merge(temp, ytdc, how='outer', on='AccountNum')
all = pd.merge(temp, actualbm, how='outer', on='AccountNum')
all = all.fillna(0)
all.AccountNum = all.AccountNum.astype(str)
all.index = range(len(all))


# %%
## left join with mapit
all, missing = mapit(all, map)


# %% [markup]
## Check actual for mismatched account names
mismatched_dict = []
for row in range(len(all)):
    a = jellyfish.jaro_distance(str(all.loc[row,'Account']), str(all.loc[row,'Accounta']))
    b = jellyfish.jaro_distance(str(all.loc[row,'Account']), str(all.loc[row,'Accountb']))
    c = jellyfish.jaro_distance(str(all.loc[row,'Account']), str(all.loc[row,'Accountc']))
    similar = max(a,b,c)
    if similar < 1:
        ## not 100% similar so add to mismatched_dict
        mismatched_dict.append(
            {
                'AccountNum': all.loc[row,'AccountNum'],
                'Similar': similar,
                'Account': all.loc[row,'Account'],
                'Account_budget': all.loc[row,'Accounta'],
                'Account_actualb': all.loc[row,'Accountb'],
                'Account_actualc': all.loc[row,'Accountc'],
            }
        )
inconsistencies = pd.DataFrame(mismatched_dict)


# %%
## select columns to keep
table = all.loc[:, ['InOrOut', 'Category', 'Account', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'SourceOfFunds', 'AccountNum']].copy()


# %% [markdown]
## Add adjustment entries for linear YTD income
apply_linear_adjustments = False
if apply_linear_adjustments == True:
    filename = 'budget_linear.xlsx'
    table = linearadj(filename, table, startb, startc, endb)


# %%
## eliminate any rows in table where all entries are $0
#mask = (table.Budget != 0) & (table.YTD != 0) & (table['Last YTD'] != 0) & (table['Current Month'] != 0)
mask = (table.Budget == 0) & (table.YTD == 0) & (table['Last YTD'] == 0) & (table['Current Month'] == 0)
table = table[-mask].copy()
table.index = range(len(table))


# %%
## sort table and add a flag for changes to category
##table = table.sort_values(by = ['Account', 'Category', 'InOrOut'], ascending=True, na_position='last')
table = table.sort_values(by = ['InOrOut', 'Category', 'Account'], ascending=True, na_position='last')
i = table.Category    
table['flag'] = i.ne(i.shift()).cumsum() % 2
table.style.apply(highlight, axis=1)


## save table to csv
table.to_csv('table.csv', index=False)


# %%
## dlh restart from here
# table = pd.read_csv('table.csv')



# %% [markdown]
# Create dataframe of table totals
table_totals = tabletotals(table)

## table_totals = table_totals.set_index(['InOrOut', 'Category'])  # create multiindex
## print(table_totals.loc[('Expense', 'Adult Ed')])                # print one index combination
## table_totals = table_totals.reset_index()                       # re-flatten multiindex


# %% [markdown]
## get summary view of table_totals
table_totals_summary = table_totals.pivot_table(index=['InOrOut', 'Category'], 
                                                values=['Budget', 'YTD', 'Last YTD'], 
                                                aggfunc=np.sum)
## not sure why, but the above creates df columns in order 'Budget', 'Last YTD', 'YTD'
## following puts them back in the order I want
table_totals_summary = table_totals_summary[['Budget', 'YTD', 'Last YTD']].copy()

'''
table_totals_summary_print = table_totals_summary.copy()
table_totals_summary_print['Budget'] = table_totals_summary_print['Budget'].apply(dollars.to_str)
table_totals_summary_print['YTD'] = table_totals_summary_print['YTD'].apply(dollars.to_str)
table_totals_summary_print['Last YTD'] = table_totals_summary_print['Last YTD'].apply(dollars.to_str)
print(table_totals_summary_print)
'''    


# %%
## export tables to Excel
## https://betterdatascience.com/style-pandas-dataframes/
## example:
##    df.style.background_gradient(cmap="RdYlGn").to_excel("table.xlsx")

## https://github.com/pandas-dev/pandas/issues/39602
'''
df = pd.DataFrame(np.random.randn(2,2), index=['Big School', 'Little School'], columns=['Data 1', 'More Data'])
df.style.format({'Data 1': '{:,.1f}', 'More Data': '{:,.3f}'})\
        .set_table_styles([{'selector': 'td', 'props': [('text-align', 'center'),
                                                        ('color', 'red')]},
                           {'selector': '.col_heading', 'props': [('text-align', 'right'),
                                                                  ('color', 'green'),
                                                                  ('width', '150px')]},
                           {'selector': '.row_heading', 'props': [('text-align', 'left'),
                                                                  ('color', 'blue')]}])
'''

filename = 'budget_out_' + str(endb) + '.xlsx'
table.style.apply(highlight, axis=1).to_excel(filename, sheet_name='budget', index=False)
## append additional sheets
with pd.ExcelWriter(filename,mode='a') as writer:  
    ## table_totals.style.apply(highlight, axis=1).to_excel(writer, sheet_name='budget_totals')
    ## table_totals_print.to_excel(writer, sheet_name='budget_totals')  # exports $ as left justified strings
    table_totals.style.apply(highlight, axis=1)\
                .to_excel(writer, sheet_name='budget_totals', index=False)           # exports $ as numbers but not currency
with pd.ExcelWriter(filename,mode='a') as writer:  
    ## table_totals_summary.style.apply(highlight, axis=1).to_excel(writer, sheet_name='budget_totals_summary')
    ## table_totals_summary_print.to_excel(writer, sheet_name='budget_totals_summary')
    table_totals_summary.to_excel(writer, sheet_name='budget_totals_summary')
    ## table_totals_summary.style.set_properties(**{'text-align': 'left'})\
    ##                    .to_excel(writer, sheet_name='budget_totals_summary')   # need index since multiindex
    ## table_totals_summary.style.set_table_styles([{'selector': '.row_heading', 'props': [('text-align', 'left')]}])\
    ##                     .to_excel(writer, sheet_name='budget_totals_summary')   # need index since multiindex
with pd.ExcelWriter(filename,mode='a') as writer:  
    actualb_read.to_excel(writer, sheet_name='actuals budget year')
with pd.ExcelWriter(filename,mode='a') as writer:  
    actualc_read.to_excel(writer, sheet_name='actuals comparison year')
with pd.ExcelWriter(filename,mode='a') as writer:  
    inconsistencies.to_excel(writer, sheet_name='inconsistencies')




# dlh end

###############################################################################
# %% [markdown]
## create plots

# %%
## collect ytdb and ytdc info by date, and in/out and category
dfactualb = actualb.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()
dfactualc = actualc.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()

## plot total income vs expense
# %%
## get list of income and expense categories from budget
budgettotals = budget.pivot_table(index=['InOrOut', 'Category'], 
                                  values=['Budget'], 
                                  aggfunc=np.sum)
categories = budgettotals.reset_index()

## sort categories so income is first then renumber categories
categories = categories.sort_values(by=['InOrOut', 'Category'], ascending=[False,True], na_position='last')
categories.index = range(len(categories))

# %%
## change year of actualc to budget year for plotting
actualc_adj = actualc.copy()
for i in range(len(actualc)):
    actualc_adj.loc[i,'Date'] = dt.date(endb.year, 
                                         actualc.loc[i,'Date'].month, 
                                         actualc.loc[i,'Date'].day)

# %% [markdown]
## Create plot for all income and expenses

# %% 
## create folder for figures if one does not already exist
path = 'figures/'
if not os.path.exists(path):
   os.makedirs(path)

## create budget in/out dataframe
endb_year = dt.date(endb.year, 12, 31)
df = budget.copy()
df = df.groupby('InOrOut').sum().abs()
df = pd.DataFrame({"Date":[startb, endb_year, startb, endb_year],
                   "Amount": [0, df.loc['Income','Budget'], 0, df.loc['Expense','Budget']],
                   "InOrOut": ['Income', 'Income', 'Expense', 'Expense']})
df['Legend'] = 'Budget'
budget_inout = df.copy()

## create same dataframe for budget year Income and Expenses
df = actualb.copy()
df = df.pivot_table(index=['InOrOut', 'Date'], values='Amount', aggfunc=np.sum).reset_index()
df.Amount = df.Amount.abs()
df.Amount = df.groupby('InOrOut')['Amount'].cumsum()
df['Legend'] = 'YTD'
actualb_inout = df.copy()

## create same dataframe for comparison year Income and Expenses
df = actualc_adj.copy()
df = df.pivot_table(index=['InOrOut', 'Date'], values='Amount', aggfunc=np.sum).reset_index()
df.Amount = df.Amount.abs()
df.Amount = df.groupby('InOrOut')['Amount'].cumsum()
df['Legend'] = 'Prior year'
actualc_inout = df.copy()

## combine
df_plots = pd.concat([budget_inout, actualb_inout, actualc_inout], axis=0)

# %%
## plot Income
df = df_plots.loc[df_plots['InOrOut'] == 'Income']
plotit(df=df, x='Date', y='Amount', hue='Legend', style='Legend', errorbar=None, 
       title='Overall Income', filename=path + 'all_income.png')

## plot Expense
df = df_plots.loc[df_plots['InOrOut'] == 'Expense']
plotit(df=df, x='Date', y='Amount', hue='Legend', style='Legend', errorbar=None, 
       title='Overall Expenses', filename=path + 'all_expenses.png')

# %%
## Income / Expense Summary Table
df = table_totals_summary.copy().reset_index()   # flatten pivot
df.loc[df['InOrOut'] == 'Income' , 'InOrOut'] = '1. Income' 
df.loc[df['InOrOut'] == 'Expense', 'InOrOut'] = '2. Expense' 
df.loc[df['InOrOut'] == '_Total' , 'InOrOut'] = '3. Grand Total' 
df = df.pivot_table(index=['InOrOut', 'Category'], 
                    values=['Budget', 'YTD', 'Last YTD'], 
                    aggfunc=np.sum)
df = df[['Budget', 'YTD', 'Last YTD']]   # pivot did not preserve this order
## df = df.sort_index(ascending=[False, True])
## following messed up the table
## df = df.style.format({'Budget'  : "${:,.0f}",
##                       'YTD'     : "${:,.0f}",
##                       'Last YTD': "${:,.0f}"}\
##                     .hide_index())
df['Budget'] = df['Budget'].apply(dollars.to_str)
df['YTD'] = df['YTD'].apply(dollars.to_str)
df['Last YTD'] = df['Last YTD'].apply(dollars.to_str)
## https://towardsdatascience.com/make-your-tables-look-glorious-2a5ddbfcc0e5
dfi.export(df, path+'all_table.png', dpi=300)    ## bug does not allow large enough table

# %%
dfi.export(df.loc[('1. Income')], path+'income_table.png', dpi=300)    ## bug does not allow large enough table
dfi.export(df.loc[('2. Expense')], path+'expense_table.png', dpi=300)    ## bug does not allow large enough table
dfi.export(df.loc[('3. Grand Total')], path+'total_table.png', dpi=300)    ## bug does not allow large enough table


# %%
see ideas here
https://stackoverflow.com/questions/35634238/how-to-save-a-pandas-dataframe-table-as-a-png


# %%
## create plots for each category
for row in range(len(categories)):
    inout = categories.loc[row, 'InOrOut']
    category = categories.loc[row, 'Category']

    ## seaborn plots and tables
    ## create dataframe of budget category as a function of time
    ## date    value legend
    ## 1/1/22  $0   budget
    ## 1/1/22  $44  budget
    ## 1/1/22  $0   Last year
    ## 1/1/22  $0   YTD

    ## extract budget value
    budget_value = budgettotals.loc[(inout, category), 'Budget']
    budget_plot = pd.DataFrame({"Date":[startb, endb_year],
                                "Amount": [0, budget_value],
                                "Legend": ['Budget', 'Budget']})
    
    ## extract actualb values
    actualb_plot = actualb.loc[(actualb['InOrOut'] == inout) & (actualb['Category'] == category),:].copy()
    actualb_plot = actualb_plot[['Date', 'Amount']]
    actualb_plot['Amount'] = actualb_plot['Amount'].cumsum()
    actualb_plot['Legend'] = 'YTD'
    
    ## extract actual values from comparison year
    actualc_plot = actualc_adj.loc[(actualc.InOrOut == inout) & (actualc.Category == category),:].copy()
    actualc_plot = actualc_plot[['Date', 'Amount']]
    actualc_plot['Amount'] = actualc_plot['Amount'].cumsum()
    actualc_plot['Legend'] = 'Last year'
    
    ## combine dataframes for plotting
    ## rbind = pd.concat([df1, df2], axis=0)
    df_plot = pd.concat([budget_plot, actualb_plot, actualc_plot], axis=0)

    ## create plot
    filename = "category_{0:01d}".format(row)
    plotit(df=df_plot, x='Date', y='Amount', hue='Legend', style='Legend', errorbar=None, 
       title=inout + ": " + category, filename=path+filename+'.png')

    ## create table
    df = table.loc[(table.InOrOut == inout) & (table.Category == category),:].copy()
    df = df.drop(['InOrOut', 'Category', 'AccountNum', 'flag'], axis=1)
    df['Budget'] = df['Budget'].apply(dollars.to_str)
    df['YTD'] = df['YTD'].apply(dollars.to_str)
    df['Last YTD'] = df['Last YTD'].apply(dollars.to_str)
    df = df.reset_index(drop=True)
    rows = len(df)
    if rows > 30:     # 19 seems to be the max for an image but fewer i
        df1 = df.iloc[range(1,15)]
        df2 = df.iloc[range(15,30)]
        df3 = df.iloc[range(30,rows)]
        dfi.export(df1, path+filename+'_table1.png', dpi=300)
        dfi.export(df2, path+filename+'_table2.png', dpi=300)
        dfi.export(df3, path+filename+'_table3.png', dpi=300)
    elif rows > 15:  # 19 seems to be the max for an image but fewer if some need double lines
        df1 = df.iloc[range(1,19)]
        df2 = df.iloc[range(19,rows)]
        dfi.export(df1, path+filename+'_table1.png', dpi=300)
        dfi.export(df2, path+filename+'_table2.png', dpi=300)
    else:
        dfi.export(df, path+filename+'_table.png', dpi=300)


# %%
## select associated table with budget, YTD, and last YTD by account
df_table = table_totals.loc[(inout, category)]
df_table.index = range(len(df_table.index))

## create plot
#fig, ax = plt.subplots(nrows=1, ncols=1)  # nrows=1 is the default
#sns.scatterplot(data=df_plot, x='assists', y='points', hue='team', ax=ax)

## add table
#table = plt.table(cellText=df.values,
#                  rowLabels=df.index,
#                  colLabels=df.columns, 
#                  ## bbox=(.2, -.7, 0.5, 0.5)) # below table
#                  bbox=(1.1, 0, 2.3, 1))       #  xmin, ymin, width, height

# %%


#fig,ax = plt.subplots(nrows=n, ncols=1, figsize=(8,11), sharex=False)  # sharex=FALSE to have different range on each x-axis
#for i in range(n):
#    plt.sca(ax[i])
#    sns.lineplot(data=df, x='assists', y='points', hue='team'
#                ).set(title= inout + " " category)
#    table = plt.table(cellText=df.values,
#                rowLabels=df.index,
#                colLabels=df.columns, 
#                bbox=(1.1, 0, 2.3, 1))       #  xmin, ymin, width, height
#    plt.tight_layout() # can be needed to avoid crowding axis labels






###############################################################################
###############################################################################
# %%


'''
## create figure object


## start over the work below with info from here:
## https://realpython.com/python-matplotlib-guide/


## extract budget value
b = multi.loc[(multi.index   == ('Expense', 'Adult Ed')) &
              (multi.Account == '_Total'), 
              'Budget'].values

fig, ax0 = plt.figure()

## set figure size
fig.set_figheight(11)
fig.set_figwidth(8)

# create grid for different subplots
spec = gridspec.GridSpec(ncols=2, nrows=2,
                         width_ratios=[1, 2], wspace=0.5,
                         hspace=0.5, height_ratios=[1, 1])
 
# initializing x,y axis value
x = [0,0]
y = ['12/31/23', b]
 
# ax0 will take 0th position in
# geometry(Grid we created for subplots),
# as we defined the position as "spec[0]"
ax0 = fig.add_subplot(spec[0])
ax0.plot(x, y)

plt.show()





# %%

## Create Table Object
ax =plt.subplots(1,1)
data=[[1,2,3],
      [9,1,8],
      [6,5,4]]
column_labels=["Col 1", "Col 2", "Col 3"]

#creating a 2-dimensional dataframe out of the given data
df=pd.DataFrame(data,columns=column_labels)

ax.axis('tight') #turns off the axis lines and labels
ax.axis('off') #changes x and y axis limits such that all data is shown

#plotting data
table = ax.table(cellText=df.values,
        colLabels=df.columns,
        rowLabels=["Row 1","Row 2","Row 3"],
        rowColours =["yellow"] * 3,
        colColours =["red"] * 3,
        loc="center")
table.set_fontsize(14)
table.scale(1,2)
plt.show()










# %%
## create figure
## https://www.geeksforgeeks.org/how-to-create-different-subplot-sizes-in-matplotlib/
from matplotlib import gridspec

# create a figure
fig = plt.figure()
 
# to change size of subplot's
# set height of each subplot as 8
fig.set_figheight(11)
 
# set width of each subplot as 8
fig.set_figwidth(8)
 
# create grid for different subplots
spec = gridspec.GridSpec(ncols=2, nrows=2,
                         width_ratios=[1, 2], wspace=0.5,
                         hspace=0.5, height_ratios=[1, 1])
 
# initializing x,y axis value
x = np.arange(0, 10, 0.1)
y = np.cos(x)
 
# ax0 will take 0th position in
# geometry(Grid we created for subplots),
# as we defined the position as "spec[0]"
ax0 = fig.add_subplot(spec[0])
ax0.plot(x, y)
 
# ax1 will take 0th position in
# geometry(Grid we created for subplots),
# as we defined the position as "spec[1]"
ax1 = fig.add_subplot(spec[1])
ax1.plot(x, y)
 
# ax2 will take 0th position in
# geometry(Grid we created for subplots),
# as we defined the position as "spec[2]"
ax2 = fig.add_subplot(spec[2])
ax2.plot(x, y)
 
# ax3 will take 0th position in
# geometry(Grid we created for subplots),
# as we defined the position as "spec[3]"
ax3 = fig.add_subplot(spec[3])
ax3.plot(x, y)
 
# display the plots
plt.show()

# %%
## Create Table Object
## https://www.scaler.com/topics/matplotlib/matplotlib-table/
fig, ax =plt.subplots(1,1)
data=[[1,2,3],
      [9,1,8],
      [6,5,4]]
column_labels=["Col 1", "Col 2", "Col 3"]

#creating a 2-dimensional dataframe out of the given data
df=pd.DataFrame(data,columns=column_labels)

ax.axis('tight') #turns off the axis lines and labels
ax.axis('off') #changes x and y axis limits such that all data is shown

#plotting data
table = ax.table(cellText=df.values,
        colLabels=df.columns,
        rowLabels=["Row 1","Row 2","Row 3"],
        rowColours =["yellow"] * 3,
        colColours =["red"] * 3,
        loc="center")
table.set_fontsize(14)
table.scale(1,2)
plt.show()



# %%
## PLOT and TABLE function
def plottable(df, title):
    '''
    # function: plottable
    # description: creates a figure object and corersponding table object
    '''
    plt.figure()
    plt.subplot(221)
    plt.plot(x, y)
    plt.yscale('linear')
    plt.title(title)
    plt.grid(True)





## pivot = table1.pivot_table(index=['InOrOut', 'Committee', 'GreenSheet'], values=['Budget', 'YTD', 'Last YTD'], aggfunc=np.sum)
for inout in ['Expense', 'Income']:
    for category in list(multi.Category)
        table = multi[(multi.InOrOut == inout) & (multi.Category == category))]
        


# %%


## Prepared dataframes: budget, actualb, actualc
for inout in ['Income', 'Expense']:
    for plot in list(budget.loc[(budget.InOrOut == inout) & (budget['Committee'].str.contains("Contributions"))]['Committee']))



##          if InOrOut == 'Income'  and    Committee       contains "Contributions", then sum "Budget" values
sum(budget.loc[(budget.InOrOut == 'Income') & (budget['Committee'].str.contains("Contributions"))]['Budget'])

## aggregate to determine total for each budget area
##      df.loc['2023'] gets all 2023 data
##      df.loc['2023', 'num'].sum() gets the total of column num in 2023
##      df['2023','num'].groupby('city').sum() gets the total of num by city
df_budget = budget.loc[daterange, 'Budget'].groupby('GreenSheet').sum()

## match income and expense line item data to budget areas






###################################################################
## OUTPUT PLOTS and TABLES

fig1 = plt.figure(1, figsize=[7,10], clear=True)  # figsize(width,height)

plt.subplot(2,2,1)    # 2 rows, 2 columns, 1st position
plt.plot([1,2,3], [1, 2, 3], color='red', label='line one', marker="o")
plt.plot([1,2,3], [4, 5, 8], color='blue', label='line two', linestyle='--')
plt.legend()

plt.subplot(2,2,2)
plt.plot([1,2,3], [1, 2, 3], color='black', label='line one', marker="o")
plt.plot([1,2,3], [4, 5, 8], color='green', label='line two', linestyle='--')
plt.legend()

## plt.show()

## figs = plt.get_fignums()
## figs

plt.savefig('fig1_singlepage.pdf')

###################
year = [2014, 2015, 2016, 2017, 2018, 2019]  
tutorial_count = [39, 117, 111, 110, 67, 29]

fig2 = plt.figure(2, figsize=[7,10], clear=True)
plt.plot(year, tutorial_count, color="#6c3376", linewidth=3)  
plt.xlabel('Year')  
plt.ylabel('Number of futurestud.io Tutorials')  

plt.savefig('fig2_singlepage.pdf')


#######################
## now put fig1 and fig2 into single PDF
## https://www.tutorialspoint.com/saving-multiple-figures-to-one-pdf-file-in-matplotlib
#plt.rcParams["figure.figsize"] = [7.00, 3.50]
#plt.rcParams["figure.autolayout"] = True
#
#fig1 = plt.figure()
#plt.plot([2, 1, 7, 1, 2], color='red', lw=5)
#
#fig2 = plt.figure()
#plt.plot([3, 5, 1, 5, 3], color='green', lw=5)

def save_multi_image(filename):
    pp = PdfPages(filename)
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()

filename = "fig_multipage.pdf"
save_multi_image(filename)

## cleanup so subsequent executions in same session do not just add to existing figures
## should not need with clear=True
## plt.get_fignums()
## fig1.clf()
## fig2.clf()


##################################
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


def niter(iterable, n):
    """
    Function that returns an n-element iterator, i.e.
    sub-lists of a list that are max. n elements long.
    """
    pos = 0
    while pos < len(iterable):
        yield iterable[pos:pos+n]
        pos += n


def plot_funcs(x, functions, funcnames, max_col, max_row):
    """
    Function that plots all given functions over the given x-range,
    max_col*max_row at a time, creating all needed figures while doing
    so.
    """

    ##amount of functions to put in one plot    
    N = max_col*max_row

    ##created figures go here
    figs = []

    ##plotted-on axes go here
    used_axes = []

    ##looping through functions N at a time:
    for funcs, names in zip(niter(functions, N), niter(funcnames,N)):

        ##figure and subplots
        fig, axes = plt.subplots(max_col, max_row)

        ##plotting functions
        for name,func,ax in zip(names, funcs, axes.reshape(-1)):
            ax.plot(x, func(x))
            ax.set_title(name)
            used_axes.append(ax)

        ##removing empty axes:
        for ax in axes.reshape(-1):
            if ax not in used_axes:
                ax.remove()

        fig.tight_layout()
        figs.append(fig)

    return figs

##some functions to display
functions = [
    lambda x: x, lambda x: 1-x, lambda x: x*x, lambda x: 1/x, #4
    np.exp, np.sqrt, np.log, np.sin, np.cos,                  #5
    ]
funcnames = ['x','1-x', 'x$^2$', '1/x', 'exp', 'sqrt', 'log', 'sin','cos']

##layout for display on the screen
disp_max_col = 3
disp_max_row = 2

##layout for pdf
pdf_max_col = 2
pdf_max_row = 4

##displaying on the screen:
x = np.linspace(0,1,100)
figs = plot_funcs(x, functions, funcnames, disp_max_row, disp_max_col)
plt.show()


##saving to pdf if user wants to:
## answer = input('Do you want to save the figures to pdf?')
answer = 'y'
if answer in ('y', 'Y', 'yes', ''):

    ##change number of subplots
    N = disp_max_col*disp_max_row
    figs = plot_funcs(x, functions, funcnames, pdf_max_row, pdf_max_col)

    ##from https://matplotlib.org/examples/pylab_examples/multipage_pdf.html
    with PdfPages('multipage_pdf.pdf') as pdf:
        for fig in figs:
            plt.figure(fig.number)
            pdf.savefig()


figs
fig
'''
