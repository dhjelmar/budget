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
##
## to enable autoreload of modules
## comment out when compile
#%reload_ext autoreload
#%autoreload 2

#%%
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
import csv

#%%
## import my functions
import modules as my

os.getcwd()


###############################################################################
#%% [markdown]
## Set Options

#%%
## Set budget and comparison year start and end dates

# overwrite above for easier date setting if not running in interactive
overwrite_dates = True
if overwrite_dates:
    print('overwriting selected dates')
    startb = dt.date(2025,  1,  1)
    endb   = dt.date(2025, 12, 31)
    startc = dt.date(2024,  1,  1)
    endc   = dt.date(2024, 12, 31)
    print('budget start    :', startb)
    print('budget end      :', endb)
    print('comparison start:', startc)
    print('comparison end  :', endc)
else:
    startb, endb, startc, endc = my.set_dates()
    # type(startb)     # datetime.date

#%% set start and end dates for pulling info from ICON
start = dt.date(2023, 1, 1)
end   = endb

#%%
interactive = True   # option used to determine function to be used for password

#%%
icon_refresh = False

#%% [markdown]
## Read Data

#%% 
# PULL INFO FROM ICON
if icon_refresh:
    print()
    print('icon_refresh = ', icon_refresh)
    print('pull data from Icon')
    actual = my.icon(start, end, interactive)
    # icon() converts string to Timestamp (same as datetime.datetime) to datetime.date
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    actual.to_csv('tmp/actual.csv', index=False)

else:
    print()
    print('icon_refresh = ', icon_refresh)
    print('pull data from saved Icon files')
    actual = pd.read_csv('tmp/actual.csv')
    # followign converts string to Timestamp (same as datetime.datetime) to datetime.date
    actual['Date'] = pd.to_datetime(actual['Date']).dt.date
    # following is only needed if the requested date ranges are smaller than what is in the csv files
    actual = actual.loc[(actual.Date >= start) & (actual.Date <= end)]
    # read from csv pulls actuals as integer so need to recovert to string for my.mapit()
    actual.AccountNum = actual.AccountNum.astype(str)

# change Date to datetime format    
actual['Date'] = pd.to_datetime(actual['Date'])

# rename Account to Account_ICON
actual = actual.rename(columns={'Account': 'Account_Icon'})

# add column for year
actual['Year'] = actual.Date.dt.year

#%%
## check for values
#print(actual.loc[actual.Account_Icon.str.contains('Endowment')])
#print(actual.loc[actual.Account_Icon.str.contains('Birch')])
#print(actual.loc[actual.Account_Icon.str.contains('Schermerhorn')])

#%% 
# READ BUDGET INFO FROM EXCEL
budget = pd.read_excel(os.path.join('input','budget.xlsx'))
budget = budget[['Year','Account','Budget']]
## extract account numbers to separate variable
budget['AccountNum'] = budget['Account'].str[:4]
# rename Account to Account_budget
budget = budget.rename(columns={'Account': 'Account_budget'})

#%%
# if budget has multiple entries per account in a given year (e.g., if additional approved later by Consistory)
# then need to collapse to one entry per account so maps correctly later
budget = budget.pivot_table(index=['Year','Account_budget','AccountNum'], 
                            values=['Budget'], 
                            aggfunc='sum').reset_index()
budget[budget.AccountNum=='4049']

#%% 
# READ MAP
print()
print("starting to read map.xlsx")
map, map_duplicates = my.read_map()
print(map[['InOrOut', 'L1', 'L2', 'Account']].head().to_string())

###############################################################################
#%% [markdown]
## Apply map

#%%
# Apply map to actuals and budget
actual, actual_missing = my.mapit(actual, map, fail_if_missing=True)
budget, budget_missing = my.mapit(budget, map, fail_if_missing=True)
#budget_missing

###############################################################################
#%% [markdown]
## Create financials object for each year and write to output file

#%%
financials = []
years = my.unique(actual.Year.to_list() + budget.Year.to_list())
for i,year in enumerate(years):
    print('i =',i,'; year =',year)
    financials.append(my.financials(year, actual, budget, map))
    financials[years.index(year)].Account.to_csv(os.path.join('output','budget_details_'+str(year)+'.csv'),
                                                 index=False)

#financials[years.index(startc.year)].similarity()
financials[years.index(startb.year)].actual


#%%
# find inconsistencies
inconsistenciesb = financials[years.index(startb.year)].similarity()
inconsistenciesc = financials[years.index(startc.year)].similarity()
all = pd.concat([inconsistenciesc, inconsistenciesb], axis=0)  # rbind
inconsistencies = all.sort_values('Similarity')
inconsistencies = inconsistencies[['Date','Account_Icon','Account_map','Amount','Similarity']]
inconsistencies.loc[inconsistencies.Similarity<0.7]


###############################################################################
#%% [markdown]
## Combine years for summary of actual amounts for eary years and 2026 budget
def modit(obj, target='Amount', levels=['InOrOut','L1']):
    if len(levels) == 2:
        df1 = obj.L1[levels+[target]].copy()
    elif len(levels) == 3:
        df1 = obj.L2[levels+[target]].copy()
    elif len(levels) == 4:
        df1 = obj.Account[levels+[target]].copy()        
    if target=='Amount':
        df1 = df1.rename(columns={target: 'Actual_'+str(obj.year)})
    else:
        df1 = df1.rename(columns={target: 'Budget_'+str(obj.year)})
    return df1

def compare_budget_2026(financials, levels=['InOrOut','L1']):
    df = pd.merge(modit(financials[years.index(2023)], levels=levels), 
                  modit(financials[years.index(2024)], levels=levels), how='outer')
    df = pd.merge(df, modit(financials[years.index(2025)], levels=levels), how='outer')
    df = pd.merge(df, modit(financials[years.index(2025)], target='Budget', levels=levels), how='outer')
    df = pd.merge(df, modit(financials[years.index(2026)], target='Budget', levels=levels), how='outer')
    df.to_csv(os.path.join('output','budget_summary.csv'), index=False)
    return df

levels=['InOrOut','L1']
levels=['InOrOut','L1','L2','Account']
df = compare_budget_2026(financials, levels=levels)
df

###############################################################################
# %% [markdown]
## Create separate dataframes for budget and comparison actuals
budget = financials[years.index(startb.year)].budget
budget = budget.drop('Year', axis='columns')
actualb = financials[years.index(startb.year)].actual
actualc = financials[years.index(startc.year)].actual


#%% [markdown]
## Write csv file with all entries from ICON combined with map info

##############################################################################
##############################################################################
######### STILL WORKING BELOW HERE TO MAKE THIS MORE OBJECT ORIENTED #########
##############################################################################
##############################################################################
# %% [markdown]
## Create summary table comparing budget and prior year (dataframe table)

#%%
print()
print("creating table for budget report")
table  = my.tableit(map, budget, actualb, actualc, 
                 startb, endb, startc)


#%%
# reorder
first = ['InOrOut', 'L1', 'L2', 'Account', 'Budget', 'Current Month', 'YTD', 'YTD%', 'Last YTD']
first = ['InOrOut', 'L1', 'L2', 'Account', 'Budget', 'YTD%', 'YTD', 'Last YTD', 'Current Month']
table = my.first(table, first)

path = os.path.join('output', 'budget_report_' + str(endb) + '_details.csv')
table.to_csv(path, index=False)
print(table[first].head().to_string())
print("find", path)

#%%
if not interactive:
    input('Press enter to exit this window')
    sys.exit()

#%%
###############################################################################
###############################################################################
###############################################################################

#%% [markdown]
## Create table_totals and plots needed for PDF file report

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
mask = ((table_totals_summary.InOrOut  != '_Total') &
       (table_totals_summary.L1 != '_Total') &
       (table_totals_summary.L2 != '_Total') &
       (table_totals_summary.Account  == '_Total'))
# mask = ((table_totals.L1 == '_Total') & (table_totals.L2 == '_Total')) | \
#        (table_totals.Account  == '_Total')
# mask = ((table_totals.L1 != '_Total') & (table_totals.L2 == '_Total')) | \
#        (table_totals.Account  == '_Total')
# invert mask
mask = ~mask
table_totals_summary = table_totals_summary.loc[mask]

#%%
# drop any row where L2 is "_Total" unless InOrOut or L1 are "_Total"
mask = ((table_totals_summary.InOrOut  != '_Total') &
       (table_totals_summary.L1 != '_Total') &
       (table_totals_summary.L2 == '_Total') &
       (table_totals_summary.Account  == '_Total'))
table_totals_summary = table_totals_summary.loc[~mask].copy()

#%%
# convert to pivot
levels=['InOrOut','L1']
table_totals_summary = table_totals_summary.pivot_table(index=levels, 
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

table_totals_summary.iloc[0:99]


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
    if (actualc.loc[i,'Date'].month==2) & (actualc.loc[i,'Date'].day==29):
        # comparison year expense was on 2/29 in a leap year so move expense to 2/28 in the adjusted non-leap year 
        actualc_adj.loc[i,'Date'] = dt.date(endb.year, 2, 28)
    else:
        # move comparison year expense to same exact day in budget year for plotting purposes
        actualc_adj.loc[i,'Date'] = dt.date(endb.year, actualc.loc[i,'Date'].month, actualc.loc[i,'Date'].day)

#%%
## identify plots to create

# all together
plots     = [{'InOrOut':'In' , 'L1':'all', 'L2':'all'}]
plots.append({'InOrOut':'Out', 'L1':'all', 'L2':'all'})

# new greensheet with personnel separate out
for committee in my.unique(table.loc[table.InOrOut=='In'].L1):
    plots.append({'InOrOut':'In', 'L1':committee, 'L2':'all'})
for committee in my.unique(table.loc[table.InOrOut=='Out'].L1):
    plots.append({'InOrOut':'Out', 'L1':committee, 'L2':'all'})


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

#%%
# table_conversion='chrome' will currently only handle tables up to 25 rows long; none of the other options are better
dfi.export(df.iloc[0:25]  , figdir + '/' + 'table_totals_summary_chrome1.png', table_conversion='chrome', dpi=300)    # bug limits to 25 max lines
if len(df) > 26:
    dfi.export(df.iloc[26:50] , figdir + '/' + 'table_totals_summary_chrome2.png', table_conversion='chrome', dpi=300)    # bug limits to 25 max lines
if len(df) > 50:
    dfi.export(df.iloc[50:75], figdir + '/' + 'table_totals_summary_chrome3.png', table_conversion='chrome', dpi=300)    # bug limits to 25 max lines
#dfi.export(table_totals_summary, figdir + '/' + 'table_totals_summary_matplotlib.png', table_conversion='matplotlib', dpi=300)    # bug limits to 25 max lines
#dfi.export(table_totals_summary, figdir + '/' + 'table_totals_summary_html2image.png', table_conversion='html2image', dpi=300)    # bug limits to 25 max lines
#dfi.export(table_totals_summary, figdir + '/' + 'table_totals_summary_playwright.png', table_conversion='playwright', dpi=300)    # bug limits to 25 max lines


#%%
# put plots into PDF
date_str =  str(endb.year) + '-' + str(endb.month) + '-' + str(endb.day)
filename = 'output/budget_report_' + date_str + '.pdf'
my.pdf(plotfiles, filename, endb, cols=2, adjust=0.99)

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


#%% [markdown]
## Experiments with better way to print df to pdf

# Function to format as currency
def format_currency(value):
    return '${:,.0f}'.format(value)
# Function to format as %
def format_percent(value):
    if value=='NA':
        value=0
    return '{:,.2%}'.format(value)

# Format col1 to 2 decimal places
# Format col3 with commas as thousands separators
formatters = {
    'Budget': format_currency,
    'YTD%': format_percent,
    'YTD': format_currency,
    'Last YTD': format_currency,
    'Current Month': format_currency}
table_totals_summary.to_html('table_totals_summary.html', formatters=formatters)


# %%

