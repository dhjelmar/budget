def pdf(path, fileout, endb, layout):
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
    from modules.imagefit import imagefit

    
    #############################################################################
    # %%
    # Global Variables
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
    fpdfx.write2pdf(pdf, 'Report date: '+today, family='Helvetica', style='B', fs=14, th=None, w=0, align='L', ln=1,
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
        
        ## starting y-location on page
        current_y = FPDF.get_y(pdf)
        
        ## print y location to screen
        print('')
        print('category', i, 'starts at y =', current_y)

        ## identify plot and corresponding table(s)
        plotfile = "category_{0:01d}_plot".format(i) + '.png'
        ## https://stackoverflow.com/questions/6930982/how-to-use-a-variable-inside-a-regular-expression
        ## tablematch = [x for x in filelist if re.findall(r'_{i}_table',x)]  # this did not work
        wanted = '_' + str(i) + '_table'
        tablematch = list(filter(lambda x: wanted in x, filelist))

        ## first get height of each plot and at least 1st table fits on page
        plt_height = Image.open(path + plotfile).height
        plt_width = Image.open(path + plotfile).width
        # scale height to pdf units
        PLOTH = PLOTW * plt_height / plt_width
        
        ## ## for loop adds up height of all tables, but some were too long for a single page so focusing just on at least one
        ## TABH = 0
        ## for tablefile in tablematch:
        ##    # get image height and width in pixels
        ##    img_height = Image.open(path + tablefile).height
        ##    img_width  = Image.open(path + tablefile).width
        ##    # scale height to pdf units
        ##    TABH = TABH + TABW * img_height / img_width

        ## figure out height of 1st table in pdf units
        # get image height and width in pixels
        img_height = Image.open(path + tablematch[0]).height
        img_width  = Image.open(path + tablematch[0]).width
        # scale height to pdf units
        TABH = TABW * img_height / img_width

        if layout == 'COL':
            category_height = max(PLOTH, TABH)
        else:
            category_height = PLOTH + th + TABH
        max_y_needed = current_y + category_height
        if max_y_needed > max_y:
            pdf.add_page()
            print('added new page to fit plot and table(s) for category', i)
            print('max_y_needed =', max_y_needed, '> max_y =', max_y)
            print('resetting current_y to top of page')
            current_y = MARGIN
            pdf.set_y(current_y)

        ## Add plot for category
        print('Adding', path + plotfile)
        pdf.image(path + plotfile, x=PLOTX, w=PLOTW)

        ## plotbottom y-location
        plotbottom = FPDF.get_y(pdf)
        print('plot bottom =', plotbottom)

        if layout != 'COL':
            pdf.ln(th)   # add a line break
            current_y = plotbottom + th

        ## Add corresponding table(s)
        for tablefile in tablematch:
            print('Adding', path + tablefile)

            ## add new page if needed to fit image
            current_y = imagefit(pdf, image=path+tablefile, wpdf=TABW, y=current_y, max_y=max_y, margin_top=MARGIN, extra=0, atleast=0)

            ## add image
            pdf.image(path + tablefile, x=TABX, y=current_y, w=TABW)   

            ## problem: get_y() not incrementing after pdf.image()
            ## suggestion to use PIL (a.k.a., pillow)
            ## https://stackoverflow.com/questions/47339043/get-y-value-of-the-image-bottom-in-fpdf-in-python
            # get image height and width in pixels
            img_height = Image.open(path + tablefile).height
            img_width  = Image.open(path + tablefile).width
            # scale height to pdf units
            TABH = TABW * img_height / img_width
            current_y = current_y + TABH
            pdf.set_y(current_y)

            current_y = FPDF.get_y(pdf)
            print('table bottom =', current_y)

        pdf.ln(th)
        current_y = FPDF.get_y(pdf)
        pdf.set_y(max(plotbottom, current_y))
        
    #############################################################################
    # Generate the PDF
    pdf.output(fileout, 'F')


# %%
