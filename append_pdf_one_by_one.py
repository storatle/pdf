#!/usr/bin/env python
"""Append pdf files to one pdf file

Merges all the given PDF files into one PDF file, in the order they are
given on the command line. The default output filename is merge_file.pdf.

Usage:
    python append_pdf_one_by_one.py file1.pdf file2.pdf file3.pdf
    python append_pdf_one_by_one.py *.pdf -o combined.pdf
    python append_pdf_one_by_one.py file1.pdf file2.pdf --open

Requirements:
    - Python 3
    - pypdf:  sudo apt install python3-pypdf  (Ubuntu/WSL)
              or  pip install pypdf  (Windows/other)
    - Optional, for --open on Linux: the Evince PDF viewer
      (sudo apt install evince). On Windows the default PDF program is used.
"""
from pypdf import PdfWriter
import argparse
import sys
import subprocess

def PDFmerge(pdfs, output):
    """Merge the PDF files in `pdfs` (in the given order) into the file `output`."""
    # PdfWriter collects pages from several PDFs and writes them as one document
    pdfWriter = PdfWriter()

    # appending pdfs one by one
    for pdf in pdfs:
        # Show which file is being processed
        print(pdf)
        # Add all pages of this PDF to the end of the merged document
        pdfWriter.append(pdf)
        # Old approach using PdfFileReader/PdfFileWriter, kept for reference:
        #with open(pdf, 'rb') as f:
#        pdfReader = PdfFileReader(f)
#        print(pdfReader.numPages)
#        for pageNum in range(pdfReader.numPages):
#            pageObj = pdfReader.getPage(pageNum)
#            pdfWriter.addPage(pageObj)

    # writing combined pdf to output pdf file
    pdfOutputfile = open(output,'wb')
    pdfWriter.write(pdfOutputfile)
    pdfOutputfile.close()

def main():
    # Set up the command line interface; the module docstring is used as help text
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # Zero or more input PDF files, merged in the order they are given
    parser.add_argument('input', help='Relative or absolute path of the input PDF file', nargs='*')
    # Name of the merged output file
    parser.add_argument('-o', '--output', default='merge_file.pdf', help='Relative or absolute path of the output PDF file, (default: merge_file.pdf)')
    # Optional flag to open the result in a PDF viewer when done
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open PDF after merging')
    args = parser.parse_args()
    # Do the actual merge
    PDFmerge(args.input, args.output)
    print('........................................')
    print('{} is written'.format(args.output))


    # Open the merged file: Explorer on Windows (uses the default PDF app),
    # otherwise the Evince document viewer (Linux)
    if args.open:
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", args.output])
        else:
            subprocess.call(["evince", args.output])



if __name__ == "__main__":
    # calling the main function
    main()
