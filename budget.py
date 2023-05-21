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
from write_excel import write_excel
from dupacct import dupacct
from dateeom import dateeom
from tabletotals import tabletotals
from plotit import plotit
from dfplot_inout import dfplot_inout

os.getcwd()


###############################################################################
# %% [markdown]
## Set budget and comparison year start and end dates
startb, endb, startc, endc = set_dates()

## set layout for plots ('COL' for columns or 'ALT' for alternating plots/tables)
layout = 'ALT'

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
from tableit import tableit
apply_linear_adjustments = False
table, inconsistencies = tableit(map, budget, actualb, actualc, 
                                 startb, endb, startc, endc,
                                 apply_linear_adjustments)


# %% [markdown]
# Create dataframe of table totals
table_totals = tabletotals(table)

## table_totals = table_totals.set_index(['InOrOut', 'Category'])  # create multiindex
## print(table_totals.loc[('Out', 'Adult Ed')])                # print one index combination
## table_totals = table_totals.reset_index()                       # re-flatten multiindex


# %% [markdown]
## get summary view of table
table_totals_summary = table.pivot_table(index=['InOrOut', 'Category'], 
                                         values=['Budget', 'YTD', 'Last YTD', 'Current Month'], 
                                         aggfunc=np.sum)
## not sure why, but the above creates df columns in order 'Budget', 'Last YTD', 'YTD'
## following puts them back in the order I want
table_totals_summary = table_totals_summary[['Budget', 'YTD', 'Last YTD', 'Current Month']].copy()
table_totals_summary = table_totals_summary.reset_index()
keepcols = table_totals_summary.columns

## add in the "_Total" rows
table_totals_summary = table_totals.loc[table_totals.Account == '_Total']
table_totals_summary = table_totals_summary[keepcols]

## sort (may not be needed) and create multi-index
table_totals_summary = table_totals_summary.sort_values(by = ['InOrOut', 'Category'], ascending=True, na_position='last')


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
filename = 'budget_out_' + str(endb) + '.xlsx'
write_excel(filename, table, table_totals, table_totals_summary, actualb, actualc, inconsistencies)



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

## create dataframe of total income and expenses by date for budget, YTD, and prior year
plot_inout = dfplot_inout(map, table, actualb, actualc_adj, 
                          startb, endb, startc, endc)

## create folder for figures if one does not already exist
path = 'figures/'
if not os.path.exists(path):
   os.makedirs(path)

## plot Income
df = plot_inout.loc[plot_inout['InOrOut'] == 'In']
plotit(df=df, x='Date', y='Amount', hue='Legend', style='Legend', errorbar=None, 
       title='Overall Income', filename=path + 'all_income.png')

## plot Expense
df = plot_inout.loc[plot_inout['InOrOut'] == 'Out']
plotit(df=df, x='Date', y='Amount', hue='Legend', style='Legend', errorbar=None, 
       title='Overall Expenses', filename=path + 'all_expenses.png')


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
actualc, junk = mapit(actualc, map)

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
    budget_plot = pd.DataFrame({"Date":[startb, dt.date(endb.year, 12, 31)],
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
    if layout == 'COL':
        figsize = (6,4)
    else:
        figsize = (11,2)
    plotit(df=df_plot, x='Date', y='Amount', hue='Legend', style='Legend', errorbar=None, 
           title=inout + ": " + category, filename=path+filename+'_plot.png', figsize=figsize)

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


###############################################################################
# %% [markdown]
## Create PDF

# %%
from pdf import pdf
fileout = 'budget_report_' + str(endb) + '.pdf'
pdf(path, fileout, endb, layout)



###############################################################################
###############################################################################
###############################################################################
###############################################################################
# %%


'''
## create figure object


## start over the work below with info from here:
## https://realpython.com/python-matplotlib-guide/


## extract budget value
b = multi.loc[(multi.index   == ('Out', 'Adult Ed')) &
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
for inout in ['Out', 'In']:
    for category in list(multi.Category)
        table = multi[(multi.InOrOut == inout) & (multi.Category == category))]
        


# %%


## Prepared dataframes: budget, actualb, actualc
for inout in ['In', 'Out']:
    for plot in list(budget.loc[(budget.InOrOut == inout) & (budget['Committee'].str.contains("Contributions"))]['Committee']))



##          if InOrOut == 'In'  and    Committee       contains "Contributions", then sum "Budget" values
sum(budget.loc[(budget.InOrOut == 'In') & (budget['Committee'].str.contains("Contributions"))]['Budget'])

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
