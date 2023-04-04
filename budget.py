# %%   # Jupyter-like notebook in text file using ipython extension and ipykernel package
###################################################################
## SETUP
import pandas as pd
import datetime as dt
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import regex as re
os.getcwd()

## ## create dataframe from two lists
## date = ['1/2/2022', '2/2/2022', '3/2/2022'] 
## nums = [10,20,30] 
## data = list(zip(date, nums)) 
## data 
## df = pd.DataFrame(data, columns=['date','nums']) 
## df

# ###################################################################
## CONTROL
## set daterange of interest
## e.g,. daterange = '2023'
##       daterange = '2022:2023'
## https://towardsdatascience.com/working-with-datetime-in-pandas-dataframe-663f7af6c587
daterange = '2023'
## pd.to_datetime(daterange)

###################################################################
# %% 
## READ BUDGET DATA

##--------------------------------------------------
## read budget file
## pd.read_excel('fn.xlsx', sheet_name=0, header=2)
budget = pd.read_excel('budget_2023.xlsx')
## budget.columns = budget.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
## only keep needed columns
budget = budget[['Income or Expence', 'Category', 'Budget category', 'Committee + Income Detail', 'Source of Funds', 'Line Items', '2023 Budget']]
budget.columns = ['InOrOut',          'Category', 'GreenSheet',      'Committee',                 'SourceOfFunds',   'Account',    'Budget']
budget['Account'] = budget['Account'].str.strip()    # strip leading and trailing white space
## create another column with budget line item number only because database not consistent with descriptions
budget['AccountNum'] = budget.Account.str.extract('(\d+)')

## ## sum totals for budget category and committee
## ## pivot table example
## df = pd.DataFrame({'Fruit': ['Apple', 'Apple', 'Banana', 'Orange'],
##                    'Stock': [10, 5, 3, 2],
##                    'Backorder': [25, 20, 10, 5]})
## df
## df.pivot_table(columns='Fruit', values=['Stock', 'Backorder'], aggfunc=np.sum)

## ## in budget, want to sum budget_2023 by 1st 3 columns
## pivot = budget.pivot_table(index=['InOrOut', 'Committee', 'GreenSheet'], values='Budget', aggfunc=np.sum)
## pivot.head()
##
## different ways to access contents
## pivot.loc[('Expense', 'Adult Ed', 'Adult Ed')]
## pivot.loc[('Expense', 'Adult Ed', 'Library')]
## pivot.loc[('Expense', 'Adult Ed')]                      # returns values in dataframe
## pivot.loc[('Expense', 'Adult Ed')].values               # returns values in np array
## sum(pivot.loc[('Expense', 'Adult Ed')].values)          # returns sum    in np array
## sum(sum(pivot.loc[('Expense', 'Adult Ed')].values))     # returns a simple sum
## pivot.iloc[[0,1]]
##
## if want to reset index to numbers and move index to dataframe columns, then
## df = pivot.reset_index()
## df_match = list(df.InOrOut == 'Income')   # creates a list of TRUE/FALSE for matches
## df.loc[df_match]

##--------------------------------------------------
# %% 
## read current year income and expense data
actual_read = pd.read_excel('revenue_expense_spreadsheet_2023.xls', header=5-1)  # header in row 5 but Python stars at row 0
actual_read = actual_read.dropna()  # option: how='all' only drops rows if all columns are na
actual_read['Account'] = actual_read['Account'].str.strip()    # strip leading and trailing white space
actual_read.columns = actual_read.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
actual_read.columns

## remove garbage lines
## ~ in the following removes the lines; no ~ would find the lines
actual_read = actual_read[-actual_read['Account'].str.contains('total|Total|Revenue|Transfers')]
## reindex dataframe to start at 0
actual_read.index = range(len(actual_read.index))
## create column of account numbers
actual_read['AccountNum'] = actual_read.Account.str.extract('(\d+)')


def stackit(df, daterange):

    nrows = len(df)
        
    ## reformat to columns of date, account, value
    ## df.head()
    accountnum  = df[['AccountNum']].copy()  # single or double bracket to create series or dataframe, respectively
    account     = df[['Account']].copy()
 
    new = []
    i = 0
    ## create accountmonth dataframe with date, account, and value for month
    for date in daterange:
        i = i+1
        ## first duplicate date using np but need to convert to a series for pandas
        daterepeated = pd.DataFrame({'Date':pd.Series(np.repeat(date, nrows))})
        value = pd.DataFrame({'Value':df.iloc[:,i]})
    
        ## https://www.geeksforgeeks.org/how-to-concatenate-two-or-more-pandas-dataframes/
        ## rbind = pd.concat([df1, df2], axis=0)
        ## cbind = pd.concat([df1, df2], axis=1)
        temp = pd.concat([daterepeated, account, accountnum, value], axis=1)
    
        if len(new) > 0: 
            ## pd.concat used as rbind in R
            new = pd.concat([new, temp], axis=0)
        else:
            new = temp

    return new

daterange = pd.date_range(start='1/1/2023', end=dt.datetime.now(), freq='M')
actual = stackit(actual_read, daterange)


##--------------------------------------------------
# %% 
## read prior year income and expense data
actual_read_old = pd.read_excel('revenue_expense_spreadsheet_2022.xls', header=5-1)  # header in row 5 but Python stars at row 0
actual_read_old = actual_read_old.dropna()  # how='all' only drops rows if all columns are na
actual_read_old['Account'] = actual_read_old['Account'].str.strip()    # strip leading and trailing white space
actual_read_old.columns = actual_read_old.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
actual_read_old.columns

## remove garbage lines
## ~ in the following removes the lines; no ~ would find the lines
actual_read_old = actual_read_old[-actual_read_old['Account'].str.contains('total|Total|Revenue|Transfers')]
## reindex dataframe to start at 0
actual_read_old.index = range(len(actual_read_old.index))

## create column of account numbers
actual_read_old['AccountNum'] = actual_read_old.Account.str.extract('(\d+)')

## reformat to columns of date, account, value
daterange_old = pd.date_range(start='1/1/2022', end='12/31/2022', freq='M')
actual_old = stackit(actual_read_old, daterange_old)

##--------------------------------------------------
# %% 
## read investment data file  (NOT CODED YET)


###################################################################
# %%
## SELECT DATA FOR DATE RANGE FROM actual AND actual_old

start = '1/1/2023'
end = '2/28/23'
actual_use = actual.loc[(actual.Date > start) & (actual.Date <= end)]

start = '1/1/2022'
end = '12/31/22'
actual_old_use = actual_old.loc[(actual_old.Date > start) & (actual_old.Date <= end)]

## add InOrOut, GreenSheet, Committee, and SourceOfFunds fields
## Need to do with if/then statements rather than merge
## Then maybe add column for Entry = ['Budget', 'Current Year', 'Prior Year']


###################################################################
# %%
## CREATE TABLE DATAFRAME FOR OUTPUT
## use pivot table to sum ytd totals
## pivot = budget.pivot_table(index=['InOrOut', 'Committee', 'GreenSheet'], values='Budget', aggfunc=np.sum)
ytd = actual_use.pivot_table(index=['AccountNum', 'Account'], values='Value', aggfunc=np.sum).reset_index()
ytd.columns = ['AccountNum', 'Account YTD', 'YTD']
ytd_old = actual_old_use.pivot_table(index=['AccountNum', 'Account'], values='Value', aggfunc=np.sum).reset_index()
ytd_old.columns = ['AccountNum', 'Account Last YTD', 'Last YTD']

'''
## Example of full outer join
a = pd.DataFrame({'Key':['one', 'two', 'three'], 'A1':['1', '2', '3'], 'A2':['4', '5', '6']})
b = pd.DataFrame({'Key':['one', 'three', 'four'], 'YTD':['10', '20', '30']})
c = pd.DataFrame({'Key':['one', 'two', 'four', 'five'], 'Last YTD':['100', '200', '300', '400']})
d = pd.merge(a, b, how='outer', on=['Key'])
e = pd.merge(d, c, how='outer', on='Key')
'''

## full, outer join (i.e., include any line item in any dataframe) for budget, ytd, and ytd_old
temp = pd.merge(budget, ytd, how='outer', on='AccountNum')
all = pd.merge(temp, ytd_old, how='outer', on='AccountNum')
all = all.fillna(0)

## select only those columns to keep and rename 1st 3 to a, b, c
keep = all.loc[:, ['InOrOut', 'Category', 'Account', 'Budget', 'YTD', 'Last YTD', 'SourceOfFunds']].copy()
keep.columns = ['a', 'b', 'c', 'Budget', 'YTD', 'Last YTD', 'SourceOfFunds']
desc = keep.loc[:, ['a', 'b', 'c', 'SourceOfFunds']]
nums = keep.loc[:, ['a', 'b', 'c', 'Budget', 'YTD', 'Last YTD']]

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
multi = pd.merge(desc, totals, how='right', on=['a', 'b', 'c'])
multi.columns = ['InOrOut', 'Category', 'Account', 'SourceOfFunds', 'Budget', 'YTD', 'Last YTD']

## create multiindex
multi = multi.set_index(['InOrOut', 'Category'])

## write details to Excel file
multi.to_excel('budget_multi.xlsx')

## print one table
print(multi.loc[('Expense', 'Adult Ed')])

# %%
## create figure object


## start over the work below with info from here:
## https://realpython.com/python-matplotlib-guide/


## set figure size
fig.set_figheight(11)
fig.set_figwidth(8)

## extract budget value
b = multi.loc[(multi.index   == ('Expense', 'Adult Ed')) &
              (multi.Account == '_Total'), 
              'Budget'].values

fig, ax0 = plt.figure()

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



'''
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
    function: plottable
    description: creates a figure object and corersponding table object
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


## Prepared dataframes: budget, actual, actual_old
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
