#!/usr/bin/env python
from pypdf import PdfReader, PdfWriter
from pypdf import PageObject
import os
import math
import argparse
import subprocess
import sys


# pdf_splitter.py
def pdf_splitter(path, split_page):
    print("Split PDF...")
    fname = os.path.splitext(os.path.basename(path))[0]
    pdf = PdfReader(path)
    if split_page == 0:
        #Split at every page
        for page in range(len(pdf.pages)):
    
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf.pages[page])
            output_filename = '{}_page_{}.pdf'.format(
                fname, page+1)
    
            with open(output_filename, 'wb') as out:
                pdf_writer.write(out)
            print('Created: {}'.format(output_filename))
            out.close()
    else:
       pdf_writer = PdfWriter()
       for page in range(split_page):
           pdf_writer.add_page(pdf.pages[page])
       output_filename = '{}_page_{}.pdf'.format(
                fname, 1)
       with open(output_filename, 'wb') as out:
           pdf_writer.write(out)
       out.close()
       print('Created: {}'.format(output_filename))
       pdf_writer = PdfWriter()
       for page in range(split_page,len(pdf.pages)):
           pdf_writer.add_page(pdf.pages[page])
       output_filename = '{}_page_{}.pdf'.format(
               fname, 2)
       with open(output_filename, 'wb') as out:
           pdf_writer.write(out)
       out.close()
       print('Created: {}'.format(output_filename))

        
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Relative or absolute path of the input PDF file')
    parser.add_argument('-o', '--out', help='Relative or absolute path of the output PDF file')
    parser.add_argument('-p', '--page', default=0, help='Split at page number')
#    parser.add_argument('-s', '--size', help='size of out paper a4 or a3')
#    parser.add_argument('-f', '--fill', action='store_true', default=False, help="Fill page if only one page")
#    parser.add_argument('--split', action='store_true', help="Split into separate files, and not merge")
    parser.add_argument('--open', action='store_true', default=False, help='Open PDF after compression')
    args = parser.parse_args()
    pdf = PdfReader(args.input)
    fname = os.path.splitext(os.path.basename(args.input))[0]
#    if not args.size:
#        args.size = "A4"
    if not args.out:
        args.out = '{}_out.pdf'.format(fname)

#    if args.split:
    pdf_splitter(args.input, int(args.page))
#    else:
#        pdf_merger(fname, args.size, pdf, args.out,args.fill)
 
    if args.open and not args.split:
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", args.out])
        else:
            subprocess.call(["evince", args.out])

if __name__ == '__main__':
   main() 
