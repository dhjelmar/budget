print('Hellow world!')
print('Hellow world2!')

print('Hellow world3!')
print('Hellow world4!')




##-----------------------------------------------------------------------------
## SETUP
import pandas as pd
import datetime

##-----------------------------------------------------------------------------
## CONTROL
## set daterange of interest
## e.g,. daterange = '2023'
##       daterange = '2022:2023'
## https://towardsdatascience.com/working-with-datetime-in-pandas-dataframe-663f7af6c587
daterange = '2023'

##-----------------------------------------------------------------------------
## READ DATA
## read budget file
budget = readexcel('xx')
budget['date'] = pd.to_datetime(budget['date'])
budget


## read income and expense data
actual = 

## read investment data file

##-----------------------------------------------------------------------------
## SELECT DATA FOR DATE RANGE
## aggregate to determine total for each budget area
##      df.loc['2023'] gets all 2023 data
##      df.loc['2023', 'num'].sum() gets the total of column num in 2023
##      df['2023','num'].groupby('city').sum() gets the total of num by city
df_budget = budget.loc[daterange, '2023 Budget'].groupby('Budget category').sum()

## match income and expense line item data to budget areas

## plot plan and actual spending as a function of time
