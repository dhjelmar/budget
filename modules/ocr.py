import pytesseract
import ocrmypdf

def ocr(pdfin, pdfout):
   '''
   adds ocr layer to PDF
   '''

   ## needed to install:
   ##   1) ghostscript from here: https://www.ghostscript.com/releases/gsdnld.html
   ##   2) path settings here: https://github.com/atlanhq/camelot/issues/465

   ## set following environment variable
   ##     TESSDATA_PREFIX='C:/Program Files/Tesseract-OCR/tesseract'
   ## OR 
   ## add following command to define the path
   ## pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  # your path may be different

   ocrmypdf.ocr(pdfin, pdfout)

ocr('budget_report_2023-04-30.pdf', 'budget_report_2023-04-30_ocr.pdf')
