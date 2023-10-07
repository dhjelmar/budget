#!/c/Users/dlhje/anaconda3/envs/py39/python
# remember to also make the script executable: chmod 755 budget.py
# execute script with: ./budget.py

## to execute file, need to:
##   1. Open VSCode
##   2. File / Open Folder / F:\Documents\01_Dave\Programs\GitHub_home\budget
##   3. Select "Run Below" in the cell below these instructions

# %%[markdown]   # Jupyter-like notebook in text file using ipython extension and ipykernel package
# # Budget Vs. Actual Spending

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
import os

## import my functions
from modules.set_dates import set_dates
from modules.read_map import read_map
from modules.read_budget import read_budget
from modules.linearadj import linearadj
from modules.mapit import mapit
from modules.icon import icon     # gives access to all function icon() in icon.py; e.g., icon(startb, endb, startc, endc)
from modules.linearadj import linearadj
import modules.dollars as dollars            # gives access to all fucntions in dollars.py; e.g., dollars.to_num('-$4')
from modules.highlight import highlight
from modules.write_excel import write_excel
from modules.dupacct import dupacct
from modules.dateeom import dateeom
from modules.tabletotals import tabletotals
from modules.plotit import plotit
from modules.dfplot_inout import dfplot_inout
from modules.rmdir import rmdir
from modules.category_plot import category_plot
from modules.category_table import category_table

os.getcwd()


###############################################################################
# %% [markdown]
## Set options

# %%
## Set budget and comparison year start and end dates
startb, endb, startc, endc = set_dates()

## set layout for plots ('COL' for columns or 'ALT' for alternating plots/tables)
layout = 'ALT'
print('layout = ', layout)

## set whether to apply linear adjustments for Covenant, Endowment, UP Fund, Tercentenary income
apply_linear_adjustments = True
print('apply_linear_adjustments = ', apply_linear_adjustments)

## set whether to update icon entries used and stored in actualb.csv or actualc.csv
icon_refresh = True
print('icon_refresh = ', icon_refresh)

###############################################################################
# %% [markdown]
## READ MAP OF ACCOUNTS TO CATEGORIES INTO DATAFRAME: map

# %%
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
if icon_refresh == True:
    actualb, actualc = icon(startb, endb, startc, endc)
    actualb.to_csv('temp_actualb.csv', index=False)
    actualc.to_csv('temp_actualc.csv', index=False)
else:
    actualb = pd.read_csv('temp_actualb.csv')
    actualc = pd.read_csv('temp_actualc.csv')
    actualb['Date'] = pd.to_datetime(actualb['Date']).dt.date
    actualc['Date'] = pd.to_datetime(actualc['Date']).dt.date
    actualb['AccountNum'] = actualb['AccountNum'].astype(str)
    actualc['AccountNum'] = actualc['AccountNum'].astype(str)
    actualb = actualb.loc[(actualb.Date >= startb) & (actualb.Date <= endb)]
    actualc = actualc.loc[(actualc.Date >= startc) & (actualc.Date <= endc)]

## add a beginning of year entry for every budget item to actualb
time0 = budget.copy()
time0.columns = ['Account', 'Amount', 'AccountNum']
time0['Date'] = startb
time0 = time0[['Date', 'Account', 'Amount', 'AccountNum']]
time0.Amount = 0
actualb = pd.concat([time0, actualb], axis=0)  # rbind
actualb.index = range(len(actualb))            # renumber dataframe
## do the same for actualc
time0['Date'] = startc
actualc = pd.concat([time0, actualc], axis=0)  # rbind
actualc.index = range(len(actualc))            # renumber dataframe


# %%
### Add adjustment entries for linear YTD income in actualb and entire year in actualc
if apply_linear_adjustments == True:
    filename = 'input_files/budget_linear.xlsx'
    actualblin, linearb = linearadj(filename, actualb, startb, endb)
    actualclin, linearc = linearadj(filename, actualc, startc, endc)
    actualb = actualblin.copy()
    actualc = actualclin.copy()

###############################################################################
# %% [markdown]
## Read investment data file  (NOT CODED YET)


###############################################################################
# %% [markdown]
## CREATE TABLE DATAFRAME FOR OUTPUT: table, table_totals

# %%
from modules.tableit import tableit
table  = tableit(map, budget, actualb, actualc, 
                 startb, endb, startc)

# %%
from modules.inconsistent import inconsistent
inconsistencies = inconsistent(map, budget, actualb, actualc, 
                               startb, endb, startc)

# %% [markdown]
# Create dataframe of table totals
table_totals = tabletotals(table)

## table_totals = table_totals.set_index(['InOrOut', 'Category'])  # create multiindex
## print(table_totals.loc[('Out', 'Adult Ed')])                # print one index combination
## table_totals = table_totals.reset_index()                       # re-flatten multiindex



# %% [markdown]
## get summary view of table
table_totals_summary = table_totals.copy()
# identify all rows to drop
mask = ((table_totals.InOrOut  != '_Total') &
       (table_totals.Category != '_Total') &
       (table_totals.Account  == '_Total'))
# invert mask
mask = ~mask
table_totals_summary = table_totals_summary.loc[mask]
# convert to pivot
table_totals_summary = table_totals_summary.pivot_table(index=['InOrOut', 'Category'], 
                                                        values=['Budget', 'YTD', 'Last YTD', 'Current Month'], 
                                                        aggfunc=np.sum)
table_totals_summary = table_totals_summary[['Budget', 'YTD', 'Last YTD', 'Current Month']]

'''
table_totals_summary_print = table_totals_summary.copy()
table_totals_summary_print['Budget'] = table_totals_summary_print['Budget'].apply(dollars.to_str)
table_totals_summary_print['YTD'] = table_totals_summary_print['YTD'].apply(dollars.to_str)
table_totals_summary_print['Last YTD'] = table_totals_summary_print['Last YTD'].apply(dollars.to_str)
print(table_totals_summary_print)
'''    

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

## first map InOrOut and Category to actualb and actualc
actualb_excel, actualb_excel_missing = mapit(actualb, map)   # add "InOrOut" and "Category" to actualb
actualc_excel, actualc_excel_missing = mapit(actualc, map)

filename = 'budget_report_' + str(endb) + '.xlsx'
write_excel(filename, table, table_totals, table_totals_summary, 
            actualb_excel, actualc_excel, inconsistencies)

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
## create dataframe of total income and expenses by date for budget, YTD, and prior year
plot_inout = dfplot_inout(map, table, actualb, actualc_adj, 
                          startb, endb, startc, endc)

# %%
## create folder for figures if one does not already exist
path = 'tmp_figures/'
#if not os.path.exists(path):
#    ## make the directory if it does not exist
#    os.makedirs(path)
#else:
#    ## clean out the directory if it does exist then make it
#    rmdir(path)
#    os.makedirs(path)
if os.path.exists(path):
    rmdir(path)
    
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
plotit(x='Date', y='Amount', data=df, vline=endb,
       hue='Legend', hue_order=hue_order, legendloc='best',
       style='Legend', markers=markers, palette=palette, 
       errorbar=None, title='Overall Income', filename=path + 'all_income.png')

## plot Expense
df = plot_inout.loc[plot_inout['InOrOut'] == 'Out']
plotit(x='Date', y='Amount', data=df, vline=endb,
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
#dfactualb, missingb = mapit(actualb, map)   # add "InOrOut" and "Category" to actualb
#dfactualc, missingc = mapit(actualc, map)
#dfactualb = dfactualb.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()
#dfactualc = dfactualc.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()

###############################################################################
# %%
## Income / Expense Summary Table
df = table_totals_summary.copy()
df['Budget'] = df['Budget'].apply(dollars.to_str)
df['YTD'] = df['YTD'].apply(dollars.to_str)
df['Last YTD'] = df['Last YTD'].apply(dollars.to_str)
df['Current Month'] = df['Current Month'].apply(dollars.to_str)
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

actualb, junk = mapit(actualb, map)
actualc_adj, junk = mapit(actualc_adj, map)

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
    df_category_fig = category_plot(inout, category, budgettotals, 
                                    startb, endb, actualb, actualc_adj, 
                                    hue_order, markers, palette, 
                                    path, fignum=row, figsize=figsize)
    plt.close('all')

    ## create table to print after plot and associated dataframe
    ## only needed if later using pdf() rather than pdf_txt()
    ## df_category_tab = category_table(inout, category, table, path, fignum=row)

# %%
'''
from modules.category_plot import category_plot
from modules.category_table import category_table
print(categories)
row = 1
inout = categories.loc[row, 'InOrOut']
category = categories.loc[row, 'Category']
endit = dt.date(2023,6,1)
df = category_plot(inout = inout, 
                   category = category, 
                   budgettotals = budgettotals, 
                   startb = startb, 
                   endb = endb, 
                   actualb = actualb, 
                   actualc_adj = actualc_adj, 
                   hue_order = hue_order, 
                   markers = markers, 
                   palette = palette, 
                   path = path, 
                   fignum=row, 
                   figsize = (11,3),
                   xlim = (startb, endit),
                   ylim = (0,200000))
'''

# %%
'''
from plotit import plotcsv
plotb = plotcsv('In', 'Contributions - pledge', 'actualb.csv')
plotc = plotcsv('In', 'Contributions - pledge', 'actualc.csv')
'''
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
