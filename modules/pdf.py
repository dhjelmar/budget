def pdf(plotfiles, fileout, endb, cols):
    '''
    Input: pngfiles = List of plot files
                      1st 2 are on 1st page along wiht summary table
                      remaining are 2 next to eachother with 6/page
           fileout  = output filename
           endb     = date for use in 1st page
    Output: PDF file

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
    HEIGHT = 297   # 11  * 25.4           # page height in mm   (was 297?)
    WIDTH  = 210   # 8.5 * 25.4           # page width in mm    (was 210?)
    MARGIN = 12
    SEPARATION = 0
    ## 2 columns split 1/2 and 1/2 for income/expense plots
    EVEN1X = MARGIN
    EVEN1W = WIDTH / 2 - MARGIN - SEPARATION/2
    EVEN2X = WIDTH / 2          + SEPARATION/2
    EVEN2W = EVEN1W
    ## set X location and full page width for a table
    TABLEX = MARGIN
    TABLEW = WIDTH - 2*MARGIN
    #TABLEH = HEIGHT - current_y - MARGINB ## set layout to specify EVEN, COL, or ALT which alternates between plots and tables

    printablew = WIDTH - 2 * MARGIN
    PLOTW = printablew / cols - (cols - 1) * SEPARATION

    # Create PDF
    ## pdf=FPDF(format='letter',unit='in')
    pdf = FPDF() # A4 (210 x 297 mm which is 8.3 x 11.7 inches)

    ## Define variable equal to text height
    th = pdf.font_size_pt
    print('text height, th =', th)
    ## pdf.ln(th)  ## add line break the same size as text

    
    def pil2mm(pil_size, dpi=72):
        # PIL images are often 72 dpi
        # need to convert to mm for FPDF
        #img = Image.open(image_path)
        #height_pixels = img.height
        height_pixels = pil_size
        height_inches = height_pixels / dpi
        height_mm = height_inches * 25.4
        return height_mm

    #############################################################################
    '''
    First Page of PDF
    '''
    # Add Page
    pdf.add_page()

    # Add lettterhead and title
    # fpdfx.create_letterhead(pdf, letterhead_picture, WIDTH)
    pdf.image("input/frcs_orig.jpg", x=WIDTH-25.4-6, y=6, w=25.4)
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
    print('current_y before add 1st figure or table', FPDF.get_y(pdf))

    ## Add income and expense figures:  pdf.image(file,x,y,w)
    #pdf.image(plotfiles[0] , x=EVEN1X, w=EVEN1W)
    #pdf.image(plotfiles[1] , x=EVEN2X, y=current_y, w=EVEN2W)
    #print('y after add in/out figures', FPDF.get_y(pdf))

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
    print('before print tables: current_y=',current_y)

    # get image heights for all 3 parts of the table to figure out sizing
    table1 = 'tmp_figures/table_totals_summary_chrome1.png'
    table2 = 'tmp_figures/table_totals_summary_chrome2.png'
    table3 = 'tmp_figures/table_totals_summary_chrome3.png'
    img1 = Image.open(table1)
    img2 = Image.open(table2)
    img3 = Image.open(table3)
    #tablew = pil2mm(img1.width)
    #table1h = pil2mm(img1.height)
    #table2h = pil2mm(Image.open(table1).height)
    #table3h = pil2mm(Image.open(table1).height)
    print()
    print('tables before scaling')
    print('img1.height=', img1.height)
    print('img2.height=', img2.height)
    print('img3.height=', img3.height)
    print('img1.width=', img1.width)
    print('img2.width=', img2.width)
    print('img3.width=', img3.width)
    # surprisingly, all 3 tables are nto the same width
    # that will complicate scaling

    # first determine scale needed to make the same width
    scalew1 = printablew / img1.width
    scalew2 = printablew / img2.width
    scalew3 = printablew / img3.width

    # next apply that to heights
    ploth1 = img1.height * scalew1
    ploth2 = img2.height * scalew2
    ploth3 = img3.height * scalew3
    plotw1 = img1.width  * scalew1
    plotw2 = img2.width  * scalew2
    plotw3 = img3.width  * scalew3
    print()
    print('tables after first scaling to get same widths')
    print('ploth1=', ploth1)
    print('ploth2=', ploth2)
    print('ploth3=', ploth3)
    print('plotw1=', plotw1)
    print('plotw2=', plotw2)
    print('plotw3=', plotw3)
    tableh = ploth1 + ploth2 + ploth3 + th    # th for slop
 
    # now scale total height to fit on page
    remaining_height = HEIGHT - current_y - MARGIN
    print('tableh          =', tableh)
    print('remaining_height=', remaining_height)
    scale2height = remaining_height / tableh

    #pdf.image(path+"all_table.png", x=MARGIN, h=TABLEH)
    ploth1 = img1.height * scalew1 * scale2height
    ploth2 = img2.height * scalew2 * scale2height
    ploth3 = img3.height * scalew3 * scale2height
    plotw1 = img1.width  * scalew1 * scale2height
    plotw2 = img2.width  * scalew2 * scale2height
    plotw3 = img3.width  * scalew3 * scale2height
    print()
    print('tables after second scaling')
    print('img1.height=', ploth1)
    print('img2.height=', ploth2)
    print('img3.height=', ploth3)
    print('img1.width=', plotw1)
    print('img2.width=', plotw2)
    print('img3.width=', plotw3)
    # not sure why this does not work right so added adjust factor to manually scale
    adjust = 1
    #pdf.image(table1, x=MARGIN, h=ploth1 * adjust)   
    #pdf.image(table2, x=MARGIN, h=ploth2 * adjust)
    #pdf.image(table3, x=MARGIN, h=ploth3 * adjust)
    pdf.image(table1, x=WIDTH/2 - plotw1/2, h=ploth1 * adjust)   
    pdf.image(table2, x=WIDTH/2 - plotw2/2, h=ploth2 * adjust)
    pdf.image(table3, x=WIDTH/2 - plotw3/2, h=ploth3 * adjust)

    # adding image does not seem to update y
    pdf.set_y(current_y + ploth1 + ploth2 + ploth3) 
    current_y = FPDF.get_y(pdf)
    print('current_y after add in/out table', current_y)
    print('total page height =', HEIGHT)


    #############################################################################
    '''
    Subsequent Pages of PDF
    '''
    ## identify list of category files
    #filelist = os.listdir(path)
    #filelist = [x for x in filelist if re.findall(r'category_',x)]
    #numplots = [x for x in filelist if re.findall(r'_plot',x)]
    #filelist = plotfiles[2:len(plotfiles)-1]  # 1st 2 png files were already printed on 1st page
    filelist = plotfiles

    # Add Page (this forces a page change; additional pages will be added as needed)
    print()
    print('###################### new page ######################')
    pdf.add_page()

    ## Add some words to PDF
    fpdfx.write2pdf(pdf, 'Detailed Income and Expense Reports', fs=14, style='B')

    position = 0
    PLOTX = MARGIN
    ## starting y-location on page
    current_y = FPDF.get_y(pdf)
    for plotfile in filelist:
                
        ## print y location to screen
        print('')
        print(plotfile, 'starts at y =', current_y)
        img = Image.open(plotfile)

        ploth = img.height * PLOTW / img.width
        remaining_y = HEIGHT - current_y - MARGIN
        remaining_y = HEIGHT - current_y
        if ploth > remaining_y:
            print()
            print('###################### new page ######################')
            pdf.add_page()
            print()
            print('added new page to fit plot and table(s) for', plotfile)
            print('plot height =', ploth, '> remaining needed =', remaining_y)
            print('resetting current_y to top of page')
            current_y = MARGIN
            pdf.set_y(current_y)
            position = 0

        ## Add income and expense figures:  pdf.image(file,x,y,w)
        #pdf.image(plotfiles[0] , x=EVEN1X, w=EVEN1W)
        #pdf.image(plotfiles[1] , x=EVEN2X, y=current_y, w=EVEN2W)
        #print('y after add in/out figures', FPDF.get_y(pdf))

        ## Add plot
        print()
        print('Adding', plotfile)
        print('current_y=',current_y)
        PLOTXi = PLOTX + position * PLOTW + SEPARATION * (cols-1)
        pdf.image(plotfile, x=PLOTXi, y=current_y, w=PLOTW)
        position = position + 1

        if position == cols:
            # increment current_y
            current_y = FPDF.get_y(pdf) + ploth
            pdf.set_y(current_y)
            # reset position
            position = 0
            # add specified amount of separation
            pdf.ln(SEPARATION)

    #############################################################################
    # Generate the PDF
    pdf.output(fileout, 'F')


# %%
