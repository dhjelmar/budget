def write_excel(filename, table, table_totals, table_totals_summary, actualb, actualc, inconsistencies):
    '''
    Writes dataframes: table, table_totals, table_totals_summary, actualb, actualc, inconsistencies
    to Excel file: filename
    '''
    import pandas as pd
    from modules.highlight import highlight
    ## https://betterdatascience.com/style-pandas-dataframes/
    ## example:
    ##    df.style.background_gradient(cmap="RdYlGn").to_excel("table.xlsx")

    ## https://github.com/pandas-dev/pandas/issues/39602
    '''
    df = pd.DataFrame(np.random.randn(2,2), index=['Big School', 'Little School'], columns=['Data 1', 'More Data'])
    df.style.format({'Data 1': '{:,.1f}', 'More Data': '{:,.3f}'})\
            .set_table_styles([{'selector': 'td', 'props': [('text-align', 'center'),
                                                            ('color', 'red')]},
                            {'selector': '.col_heading', 'props': [('text-align', 'right'),
                                                                    ('color', 'green'),
                                                                    ('width', '150px')]},
                            {'selector': '.row_heading', 'props': [('text-align', 'left'),
                                                                    ('color', 'blue')]}])
    '''

    table.style.apply(highlight, axis=1).to_excel(filename, sheet_name='budget', index=False)
    ## append additional sheets
    with pd.ExcelWriter(filename,mode='a') as writer:  
        ## table_totals.style.apply(highlight, axis=1).to_excel(writer, sheet_name='budget_totals')
        ## table_totals_print.to_excel(writer, sheet_name='budget_totals')  # exports $ as left justified strings
        table_totals.style.apply(highlight, axis=1)\
                    .to_excel(writer, sheet_name='budget_totals', index=False)           # exports $ as numbers but not currency
    with pd.ExcelWriter(filename,mode='a') as writer:  
        ## table_totals_summary.style.apply(highlight, axis=1).to_excel(writer, sheet_name='budget_totals_summary')
        ## table_totals_summary_print.to_excel(writer, sheet_name='budget_totals_summary')
        table_totals_summary.to_excel(writer, sheet_name='budget_totals_summary')
        ## table_totals_summary.style.set_properties(**{'text-align': 'left'})\
        ##                    .to_excel(writer, sheet_name='budget_totals_summary')   # need index since multiindex
        ## table_totals_summary.style.set_table_styles([{'selector': '.row_heading', 'props': [('text-align', 'left')]}])\
        ##                     .to_excel(writer, sheet_name='budget_totals_summary')   # need index since multiindex
    with pd.ExcelWriter(filename,mode='a') as writer:  
        actualb.to_excel(writer, sheet_name='actuals budget year', index=False)
    with pd.ExcelWriter(filename,mode='a') as writer:  
        actualc.to_excel(writer, sheet_name='actuals comparison year', index=False)
    with pd.ExcelWriter(filename,mode='a') as writer:  
        inconsistencies.to_excel(writer, sheet_name='inconsistencies', index=False)
