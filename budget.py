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

## import my functions
from icon import icon     # gives access to all function icon() in icon.py; e.g., icon(startb, endb, startc, endc)
import dollars            # gives access to all fucntions in dollars.py; e.g., dollars.to_num('-$4')

os.getcwd()


###############################################################################
# %% [markdown]
## Set budget and comparison year start and end dates

# %%
## https://towardsdatascience.com/working-with-datetime-in-pandas-dataframe-663f7af6c587

default = input('Press enter or escape to use current and prior year budget and comparison.\n'
                'Enter "x" (or anything else) to set start and end dates.')
if default == "":
    ## budget year to end of prior month
    startb = dt.date(dt.date.today().year, 1, 1)
    endb   = dt.date(dt.date.today().year, dt.date.today().month, 1) - dt.timedelta(days=1)
    ## comparison year
    startc = dt.date(dt.date.today().year-1, 1, 1)
    endc   = dt.date(dt.date.today().year-1, 12, 31)

else:
    startb = input('Enter start date for budget     year (mm/dd/yyyy):')
    endb   = input('Enter end   date for budget     year (mm/dd/yyyy):')
    startc = input('Enter start date for comparison year (mm/dd/yyyy):')
    endc   = input('Enter end   date for comparison year (mm/dd/yyyy):')

    ## convert to dates
    startb = dt.datetime.strptime(startb, '%m/%d/%Y').date()
    endb   = dt.datetime.strptime(endb  , '%m/%d/%Y').date()
    startc = dt.datetime.strptime(startc, '%m/%d/%Y').date()
    endc   = dt.datetime.strptime(endc  , '%m/%d/%Y').date()

yearb = startb.year
budgetfile = 'budget_' + str(yearb) + '.xlsx'
alternate = input('Press enter to use following for budget: ' + budgetfile)
if alternate != "":
    budgetfile = alternate

print('budget file     :', budgetfile)
print('budget start    :', startb)
print('budget end      :', endb)
print('comparison start:', startc)
print('comparison end  :', endc)


###############################################################################
# %% [markdown]
# ## READ BUDGET DATA INTO DATAFRAME: budget

# %%
## read budget file
## pd.read_excel('fn.xlsx', sheet_name=0, header=2)
budget = pd.read_excel(budgetfile)
## budget.columns = budget.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
## only keep needed columns
budget = budget[['Income or Expence', 'Category', 'Budget category', 'Committee + Income Detail', 'Source of Funds', 'Line Items', '2023 Budget']]

## rename columns
budget.columns = ['InOrOut',          'Category', 'GreenSheet',      'Committee',                 'SourceOfFunds',   'Account',    'Budget']
print('Renamed and kept some columns')
budget['Account'] = budget['Account'].str.strip()    # strip leading and trailing white space
## create another column with budget line item number only because database not consistent with descriptions
budget['AccountNum'] = budget.Account.str.extract('(\d+)')

print(budget.head())


###############################################################################
# %% [markdown]
## Obtain ICON entries for budget year and comparison year

# %%
# import icon.py so have access to icon()

actualb_read, actualc_read = icon(startb, endb, startc, endc)

#execfile('iconcmo-request.py')

print('budget year entries in dataframe, actualb_read:')
print(actualb_read.head())
print()
print('comparison year entries in dataframe, actualc_read:')
print(actualc_read.head())


# %%
## Map ICON entries in actualb_read and actualc_read with budget categories and collapse to month ends
## Also identify any entries with no Category in budget xlsx file

j = 0
for dfuse in [actualb_read, actualc_read]:
    df = dfuse.copy()

    ## convert Date strings to dates then push to month ends
    df.Date = pd.to_datetime(df.Date)
    for i in range(0,len(df)):
        ## following works except for December
        ##    df.Date[i] = dt.date(df.Date[i].year, df.Date[i].month+1, 1) - dt.timedelta(days=1)
        year = df.Date[i].year
        month = df.Date[i].month
        day = calendar.monthrange(year, month)[1]
        df.Date[i] = dt.date(year, month, day)
        df.at[i, 'Date'] = dt.date(year, month, day)
        

    ## extract account numbers to separate variable
    df['Account'] = df['Account'].str.strip()    # strip leading and trailing white space
    ## create another column with budget line item number only because database not consistent with descriptions
    df['AccountNum'] = df.Account.str.extract('(\d+)')

    ## map budget category to 'actualb' dataframe
    mapdf = budget.loc[:, ('InOrOut', 'Category', 'AccountNum')]
    temp = pd.merge(df, mapdf, how='left', on='AccountNum')
    df = temp

    ## flag any line items without Category assigned
    nan_values = df[df['Category'].isna()]

    if len(nan_values) == 0:
        ## budget file contains full mapping of all icon entries so proceed
        if j == 0:
            actualb = df.copy()
        else:
            actualc = df.copy()   

    else:
        ## budget file missing full mapping of all icon entries so stop
        print('')
        print('FATAL ERROR: Following ICON entries are missing a Category assignment in budget xlsx file')
        print(nan_values)
        sys.exit()

    j = j + 1

print('actualb')
print(actualb.head())
print()
print('actualc')
print(actualc.head())



###############################################################################
# %% [markdown]
## Read investment data file  (NOT CODED YET)



###############################################################################
# %% [markdown]
## CREATE TABLE DATAFRAME FOR OUTPUT: table, table_totals

# %%
## prior month expenses
actualbm = actualb.copy()
## month_prior = actualb.Date.tail(1)
## month_prior.index = range(len(month_prior))
## actualbm = actualbm.loc[actualbm['Date'] == month_prior[0]]
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
temp = pd.merge(budget, ytdb, how='outer', on='AccountNum')
temp = pd.merge(temp, ytdc, how='outer', on='AccountNum')
all = pd.merge(temp, actualbm, how='outer', on='AccountNum')
all = all.fillna(0)

## select columns to keep
table = all.loc[:, ['InOrOut', 'Category', 'Account', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'SourceOfFunds']].copy()


# %% [markdown]
# Color pandas dataframe table




# %%
## add a flag for changes to category
i = table.Category    
table['flag'] = i.ne(i.shift()).cumsum() % 2
## table = table.drop(['shade', 'count'], axis=1)

## df.style.set_properties(**{'border': '1.3px solid green',
##                           'color': 'magenta'})

#table.style.set_properties(**{'background-color': 'white',
#                          'color': 'black'})

def rowStyle(row):
    ## if row.Account == '_Total':
    ## if row.Category == 'Xbudget':
    if row.flag == 1:
        ## return ['background-color: yellow' if i else 'background-color: red' for i in is_max]
        ## return ['background-color: gray'] * len(row)
        ## return [**{'forground-color: black', 'background-color: lightgray'}] * len(row)
        ## return [('forground-color: black', 'background-color: lightgray')] * len(row)
        ## return [('forground-color: black', 'background-color: lightgray')] * len(row)
        return ['background-color: gray'] * len(row)
    return [''] * len(row)
table.style.apply(rowStyle, axis=1)


# %%
## rename 1st 3 to a, b, c
temp = table.copy()
temp.columns = ['a', 'b', 'c', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'SourceOfFunds', 'flag']
desc = temp.loc[:, ['a', 'b', 'c', 'SourceOfFunds', 'flag']]
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

table_totals.columns = ['InOrOut', 'Category', 'Account', 'SourceOfFunds', 'flag', 'Budget', 'YTD', 'Last YTD', 'Current Month']

## move flag to end
table_totals = [['InOrOut', 'Category', 'Account', 'SourceOfFunds', 'Budget', 'YTD', 'Last YTD', 'Current Month', 'flag']]

## create multiindex
table_totals = table_totals.set_index(['InOrOut', 'Category'])

## print one table
print(table_totals.loc[('Expense', 'Adult Ed')])


# %% 
## create printable versions of tables by coverting num dollars to strings with $ signs: table_totals_print

table_totals_print = table_totals.copy()
table_totals_print['Budget']   = table_totals_print['Budget'].apply(dollars.to_str)
table_totals_print['Last YTD'] = table_totals_print['Last YTD'].apply(dollars.to_str)
table_totals_print['YTD']      = table_totals_print['YTD'].apply(dollars.to_str)
table_totals_print['Current Month'] = table_totals_print['Current Month'].apply(dollars.to_str)

print(table_totals_print)


# %%
## get summary view of table_totals: table_totals_summary, table_totals_summary_print
table_totals_summary = table_totals.pivot_table(index=['InOrOut', 'Category'], 
                                                values=['Budget', 'YTD', 'Last YTD'], 
                                                aggfunc=np.sum)
## not sure why, but the above creaets df columns in order 'Budget', 'Last YTD', 'YTD'
## following puts them back in the order I want
table_totals_summary = table_totals_summary[['Budget', 'YTD', 'Last YTD']].copy()

#def dollars(x):
#    ## converts a number to currency but as a string
#   ## return "${:.1f}K".format(x/1000)
#    return "${:,.0f}".format(x)

table_totals_summary_print = table_totals_summary.copy()
table_totals_summary_print['Budget'] = table_totals_summary_print['Budget'].apply(dollars.to_str)
table_totals_summary_print['YTD'] = table_totals_summary_print['YTD'].apply(dollars.to_str)
table_totals_summary_print['Last YTD'] = table_totals_summary_print['Last YTD'].apply(dollars.to_str)

print(table_totals_summary_print)
    

# %%
## export tables to Excel
## https://betterdatascience.com/style-pandas-dataframes/
## example:
##    df.style.background_gradient(cmap="RdYlGn").to_excel("table.xlsx")

table.style.apply(rowStyle, axis=1).to_excel(r'budget_out.xlsx', sheet_name='budget', index=False)
## append additional sheets
with pd.ExcelWriter(r'budget_out.xlsx',mode='a') as writer:  
    table_totals.style.apply(rowStyle, axis=1).to_excel(writer, sheet_name='budget_totals')
with pd.ExcelWriter(r'budget_out.xlsx',mode='a') as writer:  
    table_totals_summary.style.apply(rowStyle, axis=1).to_excel(writer, sheet_name='budget_totals_summary')


###############################################################################
# %% [markdown]
## create plots

# %%
## collect ytdb and ytdc info by date, and in/out and category
dfactualb     = actualb.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()
dfactualc = actualc.groupby(['Date', 'InOrOut', 'Category']).sum().reset_index()

## seaborn plots and tables
for inout in ['Expense', 'Income']:
    for category in list(budget.Category.unique()):
        ## create dataframe of budget category as a function of time
        ## date    value legend
        ## 1/1/22  $0   budget
        ## 1/1/22  $44  budget
        ## 1/1/22  $0   prior year
        ## 1/1/22  $0   current year

        ## extract budget value
        budget_value = table_totals_summary.loc[(inout, category), 'Budget']
        dfbudget = pd.DataFrame({"Date":[startb, endb],
                                 "Amount": [0, budget_value],
                                 "Legend": ['Budget', 'Budget']})
        
        ## extract actualb values
        dfactualb = dfactualb.loc[(dfactualb.InOrOut == 'Expense') & (dfactualb.Category == 'Adult Ed'),:]
        dfactualb = dfactualb[['Date', 'Amount']]
        dfactualb.Legend = 'YTD'
        
        ## extract actualb old values
        dfactualc = dfactualc.loc[(dfactualc.InOrOut == 'Expense') & (dfactualc.Category == 'Adult Ed'),:]
        dfactualc = dfactualc[['Date', 'Amount']]
        dfactualc.Legend = 'Last YTD'
        
        ## combine dataframes for plotting
        ## rbind = pd.concat([df1, df2], axis=0)
        df_plot = pd.concat([dfbudget, dfactualb, dfactualc], axis=0)

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




#fig,ax = plt.subplots(nrows=n, ncols=1, figsize=(8,11), sharex=False)  # sharex=FALSE to have different range on each x-axis
#for i in range(n):
#    plt.sca(ax[i])
#    sns.lineplot(data=df, x='assists', y='points', hue='team'
#                ).set(title='Expense - Adult Ed\nSeaborn')
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
