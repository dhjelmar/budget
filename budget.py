#!/c/Users/dlhje/anaconda3/envs/budget/python
# remember to also make the script executable: chmod 755 budget.py
# execute script with: ./budget.py

## to execute file, need to:
##   1. Open Project using one of the following
##      a. Open VSCode
##         Select File / Open Folder / F:\Documents\01_Dave\Programs\GitHub_home\budget
##      b. Double click project folder in File Explorer
##         (double clicking budget.py in File Explorer does not open Project correctly)
##   3. Select "Run Below" in the cell below these instructions

'''
alternately, create executable with
   pyinstaller budget.py --onefile --hidden-import openpyxl.cell._writer
in linux, this creates
   budget
in windows, this creates
   budget.exe
In windows, can run by double clicking executable in file explorer
'''

# %%[markdown]   # Jupyter-like notebook in text file using ipython extension and ipykernel package
# # Budget Vs. Actual Spending

# %%
## to enable autoreload of modules
## comment out when compile
#%reload_ext autoreload
#%autoreload 2

## import packages
import pandas as pd
import datetime as dt
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import regex as re
import calendar
import dataframe_image as dfi    # had to install with pip
import jellyfish
import os

## import my functions
import modules as my

os.getcwd()


###############################################################################
# %% [markdown]
## Set options

# %%
## Set budget and comparison year start and end dates
startb, endb, startc, endc = my.set_dates()
# type(startb)     # datetime.date

# overwrite above
overwrite_dates = False
if overwrite_dates:
    startb = dt.date(2025, 1, 1)
    endb   = dt.date(2025, 1, 31)
    startc = dt.date(2024, 1, 1)
    endc   = dt.date(2024, 12, 31)

## set layout for plots ('COL' for columns or 'ALT' for alternating plots/tables)
#layout = 'ALT'
#print('layout = ', layout)

## set whether to apply linear adjustments for Covenant, Endowment, UP Fund, Tercentenary income
#apply_linear_adjustments = True
#print('apply_linear_adjustments = ', apply_linear_adjustments)

## set whether running interactively or batch
## batch = False uses getpass() for password which hides password but does not work interactively
##       = True uses input() for password which does work interactively
batch = False

## set whether to update icon entries used and stored in actualb.csv or actualc.csv
icon_refresh = False

###############################################################################
# %% [markdown]
## READ MAP OF ACCOUNTS TO CATEGORIES INTO DATAFRAME: map

# %%
print()
print("starting to read map.xlsx")
map, map_duplicates = my.read_map()
print(map[['InOrOut', 'L1', 'L2', 'Account']].head().to_string())


###############################################################################
# %% [markdown]
## READ BUDGET DATA INTO DATAFRAME: budget
print()
print("starting to read budget.xlsx")
budget, budget_duplicates = my.read_budget(startb.year)
budget = budget.rename(columns={'Account': 'Account_Budget'})

#%%
## filter budget to only requested year then drop the year column
budget = budget.loc[budget.Year==startb.year].copy()
print(budget.head().to_string())
budget = budget.drop('Year', axis='columns')

#%%
## add a budget line for checking account
#new_row = pd.DataFrame({'Account_Budget':['0000 Checking Account'], 'Budget':[0], 'AccountNum':['0000']})
#budget = pd.concat([budget, new_row], ignore_index=True)

## # %% [markdown]
## ## map categories to budget entries
## budget, missing = mapit(budget, map)

 
###############################################################################
# %% [markdown]
## Obtain ICON entries for budget year and comparison year

#%%
if icon_refresh:
    print()
    print('icon_refresh = ', icon_refresh)
    print('pull data from Icon')
    actualb, actualc = my.icon(startb, endb, startc, endc, batch)
    # icon() converts string to Timestamp (same as datetime.datetime) to datetime.date
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    actualb.to_csv('tmp/actualb.csv', index=False)
    actualc.to_csv('tmp/actualc.csv', index=False)

else:
    print()
    print('icon_refresh = ', icon_refresh)
    print('pull data from saved Icon files')
    actualb = pd.read_csv('tmp/actualb.csv')
    actualc = pd.read_csv('tmp/actualc.csv')
    # followign converts string to Timestamp (same as datetime.datetime) to datetime.date
    actualb['Date'] = pd.to_datetime(actualb['Date']).dt.date
    actualc['Date'] = pd.to_datetime(actualc['Date']).dt.date
    # following is only needed if the requested date ranges are smaller than what is in the csv files
    actualb = actualb.loc[(actualb.Date >= startb) & (actualb.Date <= endb)]
    actualc = actualc.loc[(actualc.Date >= startc) & (actualc.Date <= endc)]

# extract account numbers
actualb['AccountNum'] = actualb['Account'].str[:4]
actualc['AccountNum'] = actualc['Account'].str[:4]

# rename Account to Account_ICON
actualb = actualb.rename(columns={'Account': 'Account_Icon'})
actualc = actualc.rename(columns={'Account': 'Account_Icon'})

###############################################################################
# %% [markdown]
### READ CHECKING DATA INTO DATAFRAME: checking
#print()
#print("starting to read checking.xlsx")
#checkingfile = os.path.join('input', 'checking.xlsx')
#checking = pd.read_excel(checkingfile)
#print(checking.tail().to_string())

### income from checking for expenses
### positive means balance went down because we took money as income from checking
#checking['Account_Icon'] = '0000 Checking Account'
#balance_increase = checking['Balance'] - checking['Balance'].shift(1)
#checking['Amount'] = -balance_increase
#checking['AccountNum'] = '0000'
#checking['Year'] = checking['Date'].dt.year

### extract for each year
#checkingb = checking.loc[checking.Year==startb.year].copy()
#checkingc = checking.loc[checking.Year==startc.year].copy()
#checkingb = checkingb[['Date', 'Account_Icon', 'Amount', 'AccountNum']]
#checkingc = checkingc[['Date', 'Account_Icon', 'Amount', 'AccountNum']]

## add to actualb and actualc
#actualb = pd.concat([actualb, checkingb], ignore_index=True)
#actualc = pd.concat([actualc, checkingc], ignore_index=True)


#%%
## add a beginning of year entry for every budget item to actualb
time0 = budget.copy()
time0.columns = ['Account_Icon', 'Amount', 'AccountNum']
time0['Date'] = startb
time0 = time0[['Date', 'Account_Icon', 'Amount', 'AccountNum']]
time0.Amount = 0

#%%
actualb = pd.concat([time0, actualb], axis=0)  # rbind; this changed type from Timestamp to datetime.date
actualb.index = range(len(actualb))            # renumber dataframe
## do the same for actualc
time0['Date'] = startc
actualc = pd.concat([time0, actualc], axis=0)  # rbind
actualc.index = range(len(actualc))            # renumber dataframe

# concat messed up date format so following fixes it back to datetime.date
actualb['Date'] = pd.to_datetime(actualb['Date']).dt.date
actualc['Date'] = pd.to_datetime(actualc['Date']).dt.date
#print(type(actualc.Date[len(actualc)-1]))


# %%
'''
### Add adjustment entries for linear YTD income in actualb and entire year in actualc
if apply_linear_adjustments == True:
    filename = 'input/budget_linear.xlsx'
    actualblin, linearb = my.linearadj(filename, actualb, startb, endb)
    actualclin, linearc = my.linearadj(filename, actualc, startc, endc)
    actualb = actualblin.copy()
    actualc = actualclin.copy()
'''


#%%
## map 
## left join with mapit
actualb, missingb = my.mapit(actualb, map)
actualc, missingc = my.mapit(actualc, map)

#%%
## combine and write csv file
all = pd.concat([actualc, actualb], axis=0)  # rbind
all = all.rename(columns={'Account': 'Account_Map'})
all.columns
all.index = range(0,len(all))
similar = []
for row in range(len(all)):
    a = jellyfish.jaro_similarity(str(all.loc[row,'Account_Icon']), str(all.loc[row,'Account_Map']))
    similar.append(a)
all['Similarity'] = similar
first = ['InOrOut', 'L1', 'L2', 'Date', 'Account_Icon', 'Account_Map', 'Amount', 'Similarity']
all = my.first(all, first)
if not os.path.exists('output'):
        os.mkdir('output')

path = os.path.join('output', 'all.csv')
all.to_csv(path, index=False)
print(all[first].head().to_string())
print("find", path)


###############################################################################
# %% [markdown]
## CREATE TABLE DATAFRAME FOR OUTPUT: table, table_totals

#%%
print()
print("creating table for budget report")
table  = my.tableit(map, budget, actualb, actualc, 
                 startb, endb, startc)

# reorder
first = ['InOrOut', 'L1', 'L2', 'Account', 'Budget', 'Current Month', 'YTD', 'YTD%', 'Last YTD']
table = my.first(table, first)

table.to_csv(os.path.join('output', 'table.csv'), index=False)

path = os.path.join('output', 'table.csv')
table.to_csv(path, index=False)
print(table[first].head().to_string())
print("find", path)


#%%
# evaluate inconsistencies
print()
print("evaluating inconsistencies in account names")
inconsistencies = my.inconsistent(map, budget, actualb, actualc, 
                                  startb, endb, startc)
print(inconsistencies.head().to_string())

path = os.path.join('output', 'inconsistencies.csv')
inconsistencies.to_csv(path, index=False)
print()
print("find", path)



#%%
if batch:
    input('Press enter to exit this window')



#%%
###############################################################################
###############################################################################
###############################################################################


#%%

#%% [markdown]
# Create dataframe of table totals

#%%
table_totals = my.tabletotals(table)

## table_totals = table_totals.set_index(['InOrOut', 'L1'])  # create multiindex
## print(table_totals.loc[('Out', 'Adult Ed')])                # print one index combination
## table_totals = table_totals.reset_index()                       # re-flatten multiindex



# %% [markdown]
## get summary view of table
table_totals_summary = table_totals.copy()
# identify all rows to drop
mask = ((table_totals.InOrOut  != '_Total') &
       (table_totals.L1 != '_Total') &
       (table_totals.L2 != '_Total') &
       (table_totals.Account  == '_Total'))
# invert mask
mask = ~mask
table_totals_summary = table_totals_summary.loc[mask]
# convert to pivot
table_totals_summary = table_totals_summary.pivot_table(index=['InOrOut', 'L1', 'L2'], 
                                                        values=['Budget', 'YTD', 'Last YTD', 'Current Month'], 
                                                        aggfunc=np.sum)
# add percent of budget column
table_totals_summary['YTD%'] = table_totals_summary['YTD'] / table_totals_summary['Budget']
print(table_totals_summary.head())

# rearrange table
table_totals_summary = table_totals_summary[['Budget', 'YTD%', 'YTD', 'Last YTD', 'Current Month']]
table_totals_summary.loc[('_Total', '_Total'),'YTD%'] = 'NA'
# print(df.loc[('_Total', '_Total'),'YTD%'])
#table_totals_summary_print = table_totals_summary.copy()
#table_totals_summary_print['Budget'] = my.table_totals_summary_print['Budget'].apply(my.dollars.to_str)
#table_totals_summary_print['YTD'] = my.table_totals_summary_print['YTD'].apply(my.dollars.to_str)
#table_totals_summary_print['Last YTD'] = table_totals_summary_print['Last YTD'].apply(my.dollars.to_str)
#print(table_totals_summary_print)
   

# %%
## test error with table_totals_summary
#df = table_totals.head(20).copy()
### only keep the columns I need
#df = df[['InOrOut', 'Category', 'Budget', 'YTD', 'Last YTD', 'Current Month']]
#df.pivot_table(index=['InOrOut', 'Category'], 
#               values=['Budget', 'YTD', 'Last YTD', 'Current Month'], 
#               aggfunc=np.sum).copy()
#print(df)
#print(df.pivot_table)

# %%
## export tables to Excel

actual_reorder = ['InOrOut', 'L1', 'L2', 'Account']
actualb = my.first(actualb, actual_reorder)
actualc = my.first(actualc, actual_reorder)

filename = 'budget_report_' + str(endb) + '.xlsx'
path = os.path.join('output', filename)
my.write_excel(path, table, table_totals, table_totals_summary, 
            actualb, actualc, inconsistencies)

## actualc had the following incorrect in/out wash entries that need to be deleted


###############################################################################
# %% [markdown]
## Create Income / Expense plots


# %%
## change year of actualc to budget year for plotting
actualc_adj = actualc.copy()
for i in range(len(actualc)):
    actualc_adj.loc[i,'Date'] = dt.date(endb.year, 
                                        actualc.loc[i,'Date'].month, 
                                        actualc.loc[i,'Date'].day)

# %%

my.plot_compare('In', 'all', 'all', endb, actualb, actualc_adj, table)

my.plot_compare('Out', 'all', 'all', endb, actualb, actualc_adj, table)

InOrOut = 'Out'
L1      = 'Education, Music, & Arts'
L2      = 'Worship & Arts'
my.plot_compare(InOrOut, L1, L2, endb, actualb, actualc_adj, table)




#%%


#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################

## create dataframe of total income and expenses by date for budget, YTD, and prior year
plot_inout = my.dfplot_inout(map, table, actualb, actualc_adj, 
                             startb, endb, startc, endc)

# %%
## create folder for figures if one does not already exist
path = 'tmp_figures/'
#if not os.path.exists(path):
#    ## make the directory if it does not exist
#    os.makedirs(path)
#else:
#    ## clean out the directory if it does exist then make it
#    my.rmdir(path)
#    os.makedirs(path)
if os.path.exists(path):
    my.rmdir(path)
    
os.makedirs(path)

# %%
## plot Income
df = plot_inout.loc[plot_inout['InOrOut'] == 'In']
## following creates solid blue = 'Budget'
##                   dotted green = 'Last year'
##                   dashed red with "o" marker = 'YTD
hue_order = ['Budget', 'Last year', 'YTD']
markers = [',','o','v']    # unclear to me why this should not be [',',',','o']
palette = ['b', 'g', 'r']
my.plotit(x='Date', y='Amount', data=df, vline=endb,
       hue='Legend', hue_order=hue_order, legendloc='best',
       style='Legend', markers=markers, palette=palette, 
       errorbar=None, title='Overall Income', filename=path + 'all_income.png')

## plot Expense
df = plot_inout.loc[plot_inout['InOrOut'] == 'Out']
my.plotit(x='Date', y='Amount', data=df, vline=endb,
       hue='Legend', hue_order=hue_order, legendloc='best',
       style='Legend', markers=markers, palette=palette, 
       errorbar=None, title='Overall Expenses', filename=path + 'all_expenses.png')

# %%
## this clears plots from memory (desired)
## will also keep plots from showing in interactive mode if in same jupyter cell
plt.close('all')  

###############################################################################
# %%
### collect ytdb and ytdc info by date, and in/out and category
#dfactualb, missingb = my.mapit(actualb, map)   # add "InOrOut" and "Category" to actualb
#dfactualc, missingc = my.mapit(actualc, map)
#dfactualb = dfactualb.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()
#dfactualc = dfactualc.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()

###############################################################################
# %%
## Income / Expense Summary Table
df = table_totals_summary.copy()
df['Budget'] = df['Budget'].apply(my.dollars.to_str)
#df.style.format({
#    # 'var1%': '{:,.2f}'.format,
#    # 'var2': '{:,.2f}'.format,
#    'YTD%': '{:,.0%}'.format,
#})
# df.style.format({'YTD%': "{:.0%}"})
df['YTD%'] = df['YTD%'].apply(my.percent)
df['YTD'] = df['YTD'].apply(my.dollars.to_str)
df['Last YTD'] = df['Last YTD'].apply(my.dollars.to_str)
df['Current Month'] = df['Current Month'].apply(my.dollars.to_str)
print(df)
## https://towardsdatascience.com/make-your-tables-look-glorious-2a5ddbfcc0e5
dfi.export(df, path+'all_table.png', dpi=300)    ## bug does not allow large enough table

# %%
# bug possibly fixed
#dfi.export(df.loc[('In')], path+'income_table.png', dpi=300)    ## bug does not allow large enough table
#dfi.export(df.loc[('Out')], path+'expense_table.png', dpi=300)    ## bug does not allow large enough table
#dfi.export(df.loc[('_Total')], path+'total_table.png', dpi=300)    ## bug does not allow large enough table


# %%
## see ideas here
## https://stackoverflow.com/questions/35634238/how-to-save-a-pandas-dataframe-table-as-a-png


###############################################################################
# %% [markdown]
## create plots for each category

# %%

## get list of income and expense categories from budget
budgettotals = table.pivot_table(index=['InOrOut', 'Category'], 
                                values=['Budget'], 
                                aggfunc=np.sum)
categories = budgettotals.reset_index()

actualb, junk = my.mapit(actualb, map)
actualc_adj, junk = my.mapit(actualc_adj, map)

# %%
if layout == 'COL':
    figsize = (6,4)
else:
    ## figsize = (11,2)
    figsize = (11,3)

# %%
for row in range(len(categories)):
    ## row = 5
    inout = categories.loc[row, 'InOrOut']
    category = categories.loc[row, 'Category']

    print(' ')
    print('Starting: ', inout, ' ', category)

    ## create plot and return dataframe used for plot
    df_category_fig = my.category_plot(inout, category, budgettotals, 
                                    startb, endb, actualb, actualc_adj, 
                                    hue_order, markers, palette, 
                                    path, fignum=row, figsize=figsize)
    plt.close('all')

    ## create table to print after plot and associated dataframe
    ## only needed if later using pdf() rather than pdf_txt()
    ## df_category_tab = category_table(inout, category, table, path, fignum=row)

# %%
###############################################################################
# %% [markdown]
## Create PDF

# %%
## ## create pdf from pictures of tables
## from modules.pdf import pdf
## fileout = 'budget_report_' + str(endb) + '.pdf'
## pdf(path, fileout, endb, layout)


# %%
## create pdf by writing tables directly so they are searchable
from modules.pdf_txt import pdf_txt
fileout = 'budget_report_' + str(endb) + '.pdf'
pdf_txt(path, fileout, endb, layout, categories, table)

# %%
'''