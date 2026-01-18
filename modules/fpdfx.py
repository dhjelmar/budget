import datetime as dt
from fpdf import FPDF
import modules.fpdfx as fpdfx


def df2pdf(pdf, df, cellw=None):
    '''
    ## https://www.justintodata.com/generate-reports-with-python/
    '''
    # A cell is a rectangular area, possibly framed, which contains some text
    # Set the width and height of cell
    ## table_cell_width = 25
    table_cell_height = 6

    ## set fill color for table cell if fill=True
    pdf.set_fill_color(240,240,240)

    # Select a font as Arial, bold, 8
    pdf.set_font('Arial', 'B', 8)

    # replace any special characters in column names with underscore
    df.columns = df.columns.str.replace('[ ,!,@,#,$,%,^,&,*,(,),-,+,=,\',\"]', '_', regex=True)

    # Loop over to print column names
    cols = df.columns
    
    ## set column widths for table
    table_cell_width = []   # blank list
    i = 0
    for col in cols:
        if cellw == None:
            ## find maximum width of column name or any value in col
            width = 2.2 * max(len(col), df[col].str.len().max())
        else:
            width = cellw[i]
        ## save width in a list (will need it later)
        table_cell_width.append(width)
        ## set cell width to that width
        pdf.cell(width, table_cell_height, col, align='C', border=1)
        i = i + 1
    ## convert list to array
    ## table_cell_width = np.array(table_cell_width)
    ## no need for above because can just access list

    # Line break
    pdf.ln(table_cell_height)
    # Select a font as Arial, regular, 10
    pdf.set_font('Arial', '', 10)

    # Loop over to print each data in the table
    irow = 0
    for row in df.itertuples():
        shade = (irow + 1) % 2   # remainder operator
        icol = 0
        if shade:
            shadeit = True
        else:
            shadeit = False
        for col in cols:
            value = str(getattr(row, col))
            ## if cell contains $, right justify
            money = '$' in str(value)
            if money:
                pdf.cell(table_cell_width[icol], table_cell_height, value, align='R', border=1, fill=shadeit)
            else:
                pdf.cell(table_cell_width[icol], table_cell_height, value, align='L', border=1, fill=shadeit)
            icol = icol + 1
        pdf.ln(table_cell_height)
        irow = irow + 1



##############################################
##  Following from:
##  https://david-kyn.medium.com/workplace-automation-generate-pdf-reports-using-python-fa75c50e7715
##############################################


def create_letterhead(pdf, picture, WIDTH):
    '''
    adds letterhead pictuer and increases current y location from top
    '''
    pdf.image(picture, 0, 0, WIDTH)

def create_title(pdf, title, titleh, th):
    '''
    pdf is the page object
    title is the text to print
    titleh is the title height
    th is the text height for a single line (not the title)
    '''

    # Add main title
    pdf.set_font('Helvetica', 'b', 20)  
    pdf.ln(th)
    pdf.write(titleh, title)          # pdf.write(height, string)

    # Add main title but centered
    # Cell(??, height, string, ??, ??, 'C')  # where 'C' centers text in cell
    # unfortunately, the following does not recognize "->""
    # pdf->Cell(0, 5, "text", 0, 0, 'C')

    # Add date of report
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(r=128,g=128,b=128)
    today = str(dt.date.today())                   # YYYY-MM-DD
    # today = dt.date.today().strftime("%m/%d/%Y")   # MM/DD/YYYY
    pdf.ln(th)
    pdf.write(th, f'{today}')
    
    # Add line break
    #pdf.ln(10)

def write_to_pdf(pdf, words, th):
    
    # Set text colour, font size, and font type
    pdf.set_text_color(r=0,g=0,b=0)
    pdf.set_font('Helvetica', '', th)  # font size was 14 pt
    
    pdf.write(th, words)                # line height was 5 (not sure why there is size and height)


def write2pdf(pdf, txt, family='Helvetica', style='', fs=None, th=None, w=0, align='L', ln=1, r=0, g=0, b=0):
    '''
    writes text to pdf object using FPDF.cell function

    Input
    -----
    pdf = FPDF object
    text = string to be printed
    family = 'Courier' (default)
    style  = '' for regular text (default)
           = 'B' for bold
           = 'I' for italix)
    fs     = font size in pt. (default is 12 if th is not specified)
                              (default is to calculate as fs = th * 25/10 if th is specified)
    th     = text height      (default is to calculate as th = fs * 10/25)
    w      = width of text (default of 0 specifies entire page width)
    align  = 'L' for left justified
           = 'C' for center justified
           = 'R' for right justified
    ln     = 0 to position cursor to the right after writing text
           = 1 to position cursor to beginning of next line
           = 2 to position cursor below
    r      = red
    g      = green
    b      = blue
    '''

    ## conversion
    th2fs = 10/25   # th / fs = ratio of text height to font size

    if (fs == None) & (th == None):
        fs = 12
    
    if fs == None:
        fs = th / th2fs
    
    if th == None:
        th = fs * th2fs

    ## write to pdf
    pdf.set_font(family=family, style=style, size=fs) 
    pdf.set_text_color(r=r,g=g,b=b)
    pdf.cell(w=w, h=th, txt=txt, ln=ln, align=align)   # ln=1 is carriage return


def pdftest():
    pdf = FPDF() # A4 (210 x 297 mm which is 8.3 x 11.7 inches)
    pdf.set_margins(left=10, top=15, right=10)
    th = pdf.font_size_pt
    print('pdf.font_size_pt =', th)
    pdf.add_page()
    print('current y =', FPDF.get_y(pdf))
    # fpdfx.write2pdf(pdf, 'hello world1', fs=40)

    ## set font size
    fs = 12
    ## convert to text height, th
    h2size = 10/25
    th = fs * h2size
    pdf.set_font("Courier", size = fs) 
    pdf.cell(w=200, h=th, txt='line 1', ln=1, align= '')   # ln=1 is carriage return
    pdf.cell(w=200, h=th, txt='line 2', ln=1, align= '') 
    pdf.cell(w=200, h=th, txt='line 3', ln=1, align= 'C')  # align='C' centers text

    ## now try with write2pdf
    fpdfx.write2pdf(pdf, 'line4')
    fpdfx.write2pdf(pdf, 'line5', family='Helvetica', style='', fs=None, th=None, w=0, align='L', ln=1)
    fpdfx.write2pdf(pdf, 'line6')
    fpdfx.write2pdf(pdf, 'line7', family='Courier', style='B', fs=22, th=None, w=0, align='L', ln=1)
    fpdfx.write2pdf(pdf, 'line8')
    fpdfx.write2pdf(pdf, 'line9')
    fpdfx.write2pdf(pdf, 'line10', family='Courier', style='', fs=None, th=22, w=0, align='C', ln=1)
    fpdfx.write2pdf(pdf, 'line11')

    print('current y =', FPDF.get_y(pdf))

    ## export
    pdf.output('test.pdf', 'F')


class PDF(FPDF):
    '''
    Extends FPDF class to modify the footer function in the FPDF library
    '''
    def footer(self):
        '''
        Adds page number to PDF when invoked
        '''
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')


################################################################################
    '''
    ### To write dataframe to a png file

    import dataframe_image as dfi    # had to install with pip

    df = pd.DataFrame({
        'Date': ['2022-01-01', '2022-01-01', '2022-01-01', '2022-01-01'],
        'Open': [18, 22, 19, 14],
        'High': [20, 23, 19, 16],
        'Low': [11, 22, 15, 14],
        'Close': [18, 22, 19, 14],
        'Volume': [1000, 1111, 1900, 1400]})

    # Create a new column as Close 2 days moving average
    df['Close_200ma'] = df['Close'].rolling(2).mean()

    dfi.export(df, 'df2fig_example1.png')

    def color_pos_neg_value(value):
        if value < 0:
            color = 'red'
        elif value > 0:
            color = 'green'
        else:
            color = 'black'
        return 'color: %s' % color

    styled_df = df.style.format({'Open': "{:.0f}",
                                 'High': "{:.2f}",
                                 'Low': "${:,.0f}",
                                 'Close': "{:.2f}%"})\
                  .hide_index().bar(subset=["Volume",], color='lightgreen')\
                  .applymap(color_pos_neg_value, subset=['Close_200ma'])
    
    dfi.export(styled_df, 'df2fig_example2.png')
    
    '''