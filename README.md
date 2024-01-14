# Budget Vs. Actual Spending

## Description
+ Reads budget from Excel
+ Reads actual spending for budget and comparison years from ICONCMO API
+ Creates
    + Table and figures to compare at high level
    + Table and figures to compare for line items


## Input files expected in folder "input_files"
+ budget_yyyy.xlsx = budget file in Excel format where yyyy is the year (e.g., budget_2023.xlsx) with the following required columns. Other columns also allowed in the file but are not used.
  + Account = 4-digit number followed by name of account
              Account needs to be the same in Icon
    Budget  = Value


+ budget_linear.xlsx = Excel file with planned budget for each investment fund. The purpose of listing these accounts is to assess the budget against a linear withdrawal from those accounts regardless of whether that is what is taken or not. The "Linear Adjustment" category in the output PDF will reflect deviations from that withdrawal plan. The file has the following required columns:
  + AccountNum = 4 digit number matching budget file
  + Account_linear = 4-digit number followed by name of account;
                     Account number needs to match Account number in budget_yyyy.xlsx
  + budgetyyyy = budget value for acount where yyyy is year (e.g., budget2023)
                 need to have at least 2 of these columns for budget and comparison years
		 (budget year could come from the current budget year file with alternate coding)


+ frc_orig.jpg = FRC logo used on 1st PDF page


+ map.xlsx = Excel file identifying following that correspons to
             each AccountNum in the budget file with the following required columns:
  + InOrOut = 'In' for income; 'Out' for expenses
  + Category = user defined categorization for each Account
  + SourceOfFunds = text field generally used to identify
                    Account as 'Undesignated', 'Covenant Fund', etc.
  + Account = 4-digit number followed by name of account


## Output
+ budget_report_yyyy-mm-dd.pdf  = Excel file with plots and tables of performance to budget (e.g., [budget_report_2023-09-30.pdf](budget_report_2023-09-30.pdf))

+ budget_report_yyyy-mm-dd.xlsx = Excel file with tables of performance to budget; includes every Account entry for budget year and comparison year (e.g., [budget_report_2023-09-30.xlsx](budget_report_2023-09-30.pdf))


## Environment
+ Saved using:
  + conda activate py39
  + conda env export > environment_budget.yml
+ Recreate using:
  + conda env create -f environment_budget.yml


## Executable (not working yet)
+ Created in Git Bash using:
  + Activate environment: conda activate py39
  + deterine path to python executable: which python
    + returned: /c/Users/dlhje/anaconda3/envs/py39/python
  + Added python path as environment variable: C:\Users\dlhje\anaconda3\envs\py39\
  + Two packages needed (openpyxl maybe only needed for use of Excel)
    + pip install pyinstaller
    + conda install openpyxl
  + created executable: pyinstaller --onefile budget.py
    + if fails, try removing build folder and budget.spec file
  + executable put into folder: dist
