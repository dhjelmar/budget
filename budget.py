print('Hellow world!')
print('Hellow world2!')

print('Hellow world3!')
print('Hellow world4!')

import pandas as pd 
df = pd.read_excel('fn.xlsx') # need xlrd package? 
print('df') 
date = ['1/2/2022', '2/2/2022', '3/2/2022'] 
nums = [10,20,30] 
data = list(zip(date, nums)) 
data 
df = pd.DataFrame(data, columns=['date','nums']) 
df


###################################################################
## SETUP
import pandas as pd
import datetime
import seaborn as sbn
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

###################################################################
## CONTROL
## set daterange of interest
## e.g,. daterange = '2023'
##       daterange = '2022:2023'
## https://towardsdatascience.com/working-with-datetime-in-pandas-dataframe-663f7af6c587
daterange = '2023'

###################################################################
## READ DATA

##--------------------------------------------------
## read budget file
## pd.read_excel('fn.xlsx', sheet_name=0, header=2)
budget = pd.read_excel('budget_2023.xlsx')
budget.columns = budget.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)

## rename budget.2023_budget to budget.budget_2023


## pivot table
## https://builtin.com/data-science/pandas-pivot-tables
## in budget, want to sum budget_2023 by 1st 3 columns

print(budget)
budget['date'] = pd.to_datetime(budget['date'])
budget

##--------------------------------------------------
## read current year income and expense data
actual = pd.read_excel('revenue_expense_spreadsheet_2023.xls', header=5-1)  # header in row 5 but Python stars at row 0
actual = actual.dropna(how='all')  # how='all' only drops rows if all columns are na
actual.columns = actual.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
actual.columns

## reformat to columns of date, account, value

##--------------------------------------------------
## read prior year income and expense data
actual_prior = pd.read_excel('revenue_expense_spreadsheet_2022.xls', header=5-1)  # header in row 5 but Python stars at row 0
actual = actual.dropna(how='all')  # how='all' only drops rows if all columns are na
actual.columns = actual.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)
actual.columns

## reformat to columns of date, account, value

##--------------------------------------------------
## read investment data file


###################################################################
## SELECT DATA FOR DATE RANGE
## aggregate to determine total for each budget area
##      df.loc['2023'] gets all 2023 data
##      df.loc['2023', 'num'].sum() gets the total of column num in 2023
##      df['2023','num'].groupby('city').sum() gets the total of num by city
df_budget = budget.loc[daterange, 'budget'].groupby('account').sum()

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

    ##amount of functions  to put in one plot    
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
