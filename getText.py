#!/usr/bin/env python3

# importing required modules
from pypdf import PdfReader
import os
import argparse

def pdf2txt(path):
    fname = os.path.splitext(os.path.basename(path))[0]
    # creating a pdf reader object
    reader = PdfReader(path)

# printing number of pages in pdf file
    print(len(reader.pages))

    for page in reader.pages:
        # getting a specific page from the pdf file
        # page = reader.pages[pageNum]
        # extracting text from page
        text = page.extract_text()
        print(text)
def main():

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Relative or absolute path of the input PDF file')
    parser.add_argument('-o', '--out', help='Relative or absolute path of the output PDF file')
    args = parser.parse_args()
    pdf = PdfReader(args.input)
    fname = os.path.splitext(os.path.basename(args.input))[0]
#    if not args.size:
#        args.size = "A4"
    if not args.out:
        args.out = '{}_out.txt'.format(fname)

    pdf2txt(args.input)
if __name__ == '__main__':
   main()    
