#!/usr/bin/env python3

import pypdf
import argparse

parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
parser.add_argument('input', help='Relative or absolute path of the input PDF file', nargs='*')
args = parser.parse_args()
 
pdfIn = open(args.input[0], 'rb') # exchange the 'original.pdf' with a name of your file 
pdfReader = pypdf.PdfReader(pdfIn)
pdfWriter = pypdf.PdfWriter()

for pageNum in range(len(pdfReader.pages)):
    page = pdfReader.pages[pageNum]
    page.rotate(90)
    pdfWriter.add_page(page)

pdfOut = open('rotated.pdf', 'wb')
pdfWriter.write(pdfOut)
pdfOut.close()
pdfIn.close()
