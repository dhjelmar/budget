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
import sys

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
    print('overwriting selected dates')
    startb = dt.date(2025, 1, 1)
    endb   = dt.date(2025, 1, 31)
    startc = dt.date(2024, 1, 1)
    endc   = dt.date(2024, 12, 31)

## set whether to apply linear adjustments for Covenant, Endowment, UP Fund, Tercentenary income
#apply_linear_adjustments = True
#print('apply_linear_adjustments = ', apply_linear_adjustments)

## set whether running interactively or batch
## batch = False uses getpass() for password which hides password but does not work interactively
##       = True uses input() for password which does work interactively
batch = True

## set whether to update icon entries used and stored in actualb.csv or actualc.csv
icon_refresh = True


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

path = os.path.join('output', 'budget_report_' + str(endb) + '_dated_entries.csv')
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
first = ['InOrOut', 'L1', 'L2', 'Account', 'Budget', 'YTD%', 'YTD', 'Last YTD', 'Current Month']
table = my.first(table, first)

path = os.path.join('output', 'budget_report_' + str(endb) + '_details.csv')
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

path = os.path.join('output', 'budget_report_' + str(endb) + '_inconsistencies.csv')
inconsistencies.to_csv(path, index=False)
print()
print("find", path)


#%%
if batch:
    input('Press enter to exit this window')
    sys.exit()

#%%
###############################################################################
###############################################################################
###############################################################################

#%% [markdown]
## Create tables and plots needed for PDF file report

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
#%%
## identify plots to create
plots     = [{'InOrOut':'In' , 'L1':'all', 'L2':'all'}]
plots.append({'InOrOut':'Out', 'L1':'all', 'L2':'all'})
#
plots.append({'InOrOut':'In', 'L1':'Education, Music, & Arts', 'L2':'Tercentenary Fund'})
plots.append({'InOrOut':'Out', 'L1':'Education, Music, & Arts', 'L2':'all'})
#
plots.append({'InOrOut':'In', 'L1':'Mission', 'L2':'all'})
plots.append({'InOrOut':'Out', 'L1':'Mission', 'L2':'all'})
#plots.append({'InOrOut':'In', 'L1':'Mission', 'L2':'Covenant Fund'})
#plots.append({'InOrOut':'In', 'L1':'Mission', 'L2':'UP Mission Fund'})
#
plots.append({'InOrOut':'In', 'L1':'Operations', 'L2':'all'})
plots.append({'InOrOut':'In', 'L1':'Operations', 'L2':'Contributions - pledge'})
#
# committees
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Adult Ed'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Archives'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Care & Support'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Communications'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Finance'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Membership'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Office'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Property'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Worship & Arts'})
plots.append({'InOrOut':'Out', 'L1':'Operations', 'L2':'Youth Ed'})
plots.append({'InOrOut':'Out', 'L1':'Personnel' , 'L2':'all'})

#%%
# create plots
## create folder for figures if one does not already exist
figdir = 'tmp_figures'
if os.path.exists(figdir):
    my.rmdir(figdir)
os.makedirs(figdir)

dfb = []
plotsum = []
plotfiles = []
for myplot in plots:
    InOrOut = myplot['InOrOut']
    L1      = myplot['L1']
    L2      = myplot['L2']
    path = os.path.join(figdir, InOrOut + '_' + L1 + '_' + L2 + '.png')
    plotfiles.append(path)
    dfb_ytd = my.plot_compare(InOrOut, L1, L2, endb, actualb, actualc_adj, table, path)
    dfb.append(dfb_ytd)


#%%
# put summary into png files
df = table_totals_summary.copy()
df['Budget'] = df['Budget'].apply(my.dollars.to_str)
# the following works, but my.percent() is better
#na_mask = df["YTD%"].notnull() & (df['YTD%'] != 'NA')
#df.loc[na_mask, "YTD%"] = (df.loc[na_mask, "YTD%"]*100).astype('float64').round().astype(int)
df['YTD%'] = df['YTD%'].apply(my.percent)
df['YTD'] = df['YTD'].apply(my.dollars.to_str)
df['Last YTD'] = df['Last YTD'].apply(my.dollars.to_str)
df['Current Month'] = df['Current Month'].apply(my.dollars.to_str)
# table_conversion='chrome' will currently only handle tables up to 25 rows long; none of the other options are better
dfi.export(df.iloc[0:13]  , figdir + '/' + 'table_totals_summary_chrome1.png', table_conversion='chrome', dpi=300)    # bug limits to 25 max lines
dfi.export(df.iloc[14:32] , figdir + '/' + 'table_totals_summary_chrome2.png', table_conversion='chrome', dpi=300)    # bug limits to 25 max lines
dfi.export(df.iloc[33:100], figdir + '/' + 'table_totals_summary_chrome3.png', table_conversion='chrome', dpi=300)    # bug limits to 25 max lines
#dfi.export(table_totals_summary, figdir + '/' + 'table_totals_summary_matplotlib.png', table_conversion='matplotlib', dpi=300)    # bug limits to 25 max lines
#dfi.export(table_totals_summary, figdir + '/' + 'table_totals_summary_html2image.png', table_conversion='html2image', dpi=300)    # bug limits to 25 max lines
#dfi.export(table_totals_summary, figdir + '/' + 'table_totals_summary_playwright.png', table_conversion='playwright', dpi=300)    # bug limits to 25 max lines


#%%
# put plots into PDF
date_str =  str(endb.year) + '-' + str(endb.month) + '-' + str(endb.day)
filename = 'output/budget_report_' + date_str + '.pdf'
my.pdf(plotfiles, filename, endb, cols=2)

#%%
# put detailed table into PDF


#%%

# %%
'''
## create pdf by writing tables directly so they are searchable; this was successful but not currently using it
from modules.pdf_txt import pdf_txt
fileout = 'test.pdf'
pdf_txt(path, fileout, endb, layout, categories, table)
'''
