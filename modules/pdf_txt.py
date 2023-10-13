def pdf_txt(path, fileout, endb, layout, categories, table):
    '''
    Create PDF of figures in path
    https://pyfpdf.readthedocs.io/en/latest/reference/image/index.html
    '''
    
    # %%
    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import re
    from fpdf import FPDF
    import modules.fpdfx as fpdfx
    from PIL import Image
    import dataframe_image as dfi   # had to install with pip
    import datetime as dt
    ## from modules.imagefit import imagefit
    import dataframe_image as dfi    # had to install with pip
    import modules.dollars as dollars
    from modules.percent import percent
    
    #############################################################################
    # %%
    # Global Variables
    ytd_percent = (endb-dt.date(endb.year-1, 12, 31))/dt.timedelta(365,0,0,0)
    ytd_percent = percent(ytd_percent, decimals=0)
    TITLE = "FRCS Budget Report: " + str(endb)
    WIDTH = 210
    MARGIN = 12
    SEPARATION = 2
    ## 2 columns split 1/2 and 1/2 for income/expense plots
    EVEN1X = MARGIN
    EVEN1W = WIDTH / 2 - MARGIN - SEPARATION/2
    EVEN2X = WIDTH / 2          + SEPARATION/2
    EVEN2W = EVEN1W
    ## set layout for detail plots
    if layout == 'COL':
        ## 2 columns split 1/3 and 2/3
        PLOTX = MARGIN
        PLOTW = WIDTH / 3 - MARGIN - SEPARATION
        TABX = PLOTX + PLOTW + SEPARATION
        TABW = WIDTH - TABX - MARGIN
    else:
        ## alternate plots then tables
        PLOTX = MARGIN
        PLOTW = WIDTH - MARGIN*2
        TABX = PLOTX
        TABW = PLOTW
    ## set layout to specify EVEN, COL, or ALT which alternates between plots and tables
    HEIGHT = 297

    # Create PDF
    ## pdf=FPDF(format='letter',unit='in')
    pdf = FPDF() # A4 (210 x 297 mm which is 8.3 x 11.7 inches)

    ## Define variable equal to text height
    th = pdf.font_size_pt
    print('text height, th =', th)
    ## pdf.ln(th)  ## add line break the same size as text

    
    #############################################################################
    '''
    First Page of PDF
    '''
    # Add Page
    pdf.add_page()

    # Add lettterhead and title
    # fpdfx.create_letterhead(pdf, letterhead_picture, WIDTH)
    pdf.image("input_files/frcs_orig.jpg", x=WIDTH-25.4-6, y=6, w=25.4)
    #fpdfx.create_title(pdf, TITLE, 40, th)

    # Add some words to PDF
    #fpdfx.write_to_pdf(pdf, "1. Summary Statement", th)
    #pdf.ln(th)

    ## reset current y to the top of the page
    pdf.set_y(0)

    ## add title
    pdf.ln(th)
    fpdfx.write2pdf(pdf, TITLE, family='Helvetica', style='B', fs=20, th=None, w=0, align='L', ln=1)

    ## add today
    today = str(dt.date.today())                   # YYYY-MM-DD
    fpdfx.write2pdf(pdf, 
                    ytd_percent + ' through the year; Report generated on ' + today,
                    family='Helvetica', style='B', fs=14, th=None, w=0, align='L', ln=1,
                    r=128, g=128, b=128)

    ## get current y location
    current_y = FPDF.get_y(pdf)
    print('y before add in/out figures', FPDF.get_y(pdf))

    # Add income and expense figures:  pdf.image(file,x,y,w)
    pdf.image(path+"all_income.png"  , x=EVEN1X, w=EVEN1W)
    pdf.image(path+"all_expenses.png", x=EVEN2X, y=current_y, w=EVEN2W)
    print('y after add in/out figures', FPDF.get_y(pdf))

    ## if want to play with centering table, could base x on image width and scaled size
    ##        ## get image
    ##        filepath = path + "category_{0:01d}_plot".format(i)
    ##        img = Image.open(filepath)
    ##
    ##        ## get width and height
    ##        plotw = img.width
    ##        ploth = img.height

    # Add income/expense table
    ## pdf.ln(th/2)                               # pdf.ln(th) increments current y by th
    current_y = FPDF.get_y(pdf)
    MARGINB = 2*MARGIN
    TABLEH = HEIGHT - current_y - MARGINB
    pdf.image(path+"all_table.png", x=MARGIN, h=TABLEH)
    print('y after add in/out table', FPDF.get_y(pdf))

    max_y = FPDF.get_y(pdf)
    print('max y =', max_y)
    print('assumed bottom margin =', MARGINB)

    #############################################################################
    '''
    Subsequent Pages of PDF
    '''
    ## identify list of category files
    filelist = os.listdir(path)
    filelist = [x for x in filelist if re.findall(r'category_',x)]
    numplots = [x for x in filelist if re.findall(r'_plot',x)]

    # Add Page (this forces a page change; additional pages will be added as needed)
    pdf.add_page()

    ## Add some words to PDF
    fpdfx.write2pdf(pdf, 'Detailed Income and Expense Reports', fs=14, style='B')

    for i in range(0, len(numplots)):
        
        ## print y location to screen
        print('')
        print('category', i, 'starts at y =', current_y)

        ## identify plot and corresponding table(s)
        plotfile = "category_{0:01d}_plot".format(i) + '.png'
        ## https://stackoverflow.com/questions/6930982/how-to-use-a-variable-inside-a-regular-expression
        ## tablematch = [x for x in filelist if re.findall(r'_{i}_table',x)]  # this did not work
        ## wanted = '_' + str(i) + '_table'
        ## tablematch = list(filter(lambda x: wanted in x, filelist))

        ## Add plot for category
        print('Adding', path + plotfile)
        pdf.image(path + plotfile, x=PLOTX, w=PLOTW)

        ## Add corresponding table
        inout = categories.loc[i, 'InOrOut']
        category = categories.loc[i, 'Category']
        df = table.loc[(table.InOrOut == inout) & (table.Category == category),:].copy()
        ## if Account = NaN, then replace it with AccountNum
        df.loc[df['Account'].isnull(), 'Account'] = df['AccountNum']
        df = df.drop(['InOrOut', 'Category', 'AccountNum', 'flag'], axis=1)
        df['Budget'] = df['Budget'].apply(dollars.to_str)
        df['YTD'] = df['YTD'].apply(dollars.to_str)
        df['Last YTD'] = df['Last YTD'].apply(dollars.to_str)
        df['Current Month'] = df['Current Month'].apply(dollars.to_str)
        df = df.reset_index(drop=True)
        fpdfx.df2pdf(pdf, df, cellw=[80,17,17,17,23,32])

        pdf.ln(th)
        
    #############################################################################
    # Generate the PDF
    pdf.output(fileout, 'F')


# %%
