# Budget Vs. Actual Spending

## Description
+ Reads budget from Excel
+ Reads actual spending for budget and comparison years from ICONCMO API
+ Creates
    + Table and figures to compare at high level
    + Table and figures to compare for line items


## Input files
+ budget_2023.xlsx = budget file in Excel format with the following required columns:
  + InOrOut = 'In' for income; 'Out' for expenses
  + Category = user defined categorization for each Account
  + SourceOfFunds = text field generally used to identify
                    Account as 'Undesignated', 'Covenant Fund', etc.
  + Account       = 4-digit number followed by name of account
                    Account needs to be the same in Icon


+ budget_linear.xlsx = Excel file with planned budget for each investment fund with the following required columns:
  + AccountNum = 4 digit number matching budget file
  + Account_linear
  + budgetyyyy = budget value for acount where yyyy is year (e.g., budget2023)
                 need to have at least 2 of these columns for budget and comparison years


+ map.xlsx = Excel file identifying following that correspons to
             each AccountNum in the budget file with the following required columns:
  + InOrOut = 'In' for income; 'Out' for expenses
  + Category = user defined categorization for each Account
  + SourceOfFunds = text field generally used to identify
                    Account as 'Undesignated', 'Covenant Fund', etc.


+ frc_orig.jpg = FRC logo used on 1st PDF page
