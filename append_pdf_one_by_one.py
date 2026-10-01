#!/usr/bin/env python
"""Append pdf files to one pdf file
Merge all given files into one pdf-file.
Default filenane is merge_file.pdf
"""
from PyPDF2 import PdfMerger
import argparse
import sys
import subprocess

def PDFmerge(pdfs, output):
    """Merge the PDF files in `pdfs` (in the given order) into the file `output`."""
    # PdfMerger collects pages from several PDFs and writes them as one document
    pdfMerger = PdfMerger()
#    pdfWriter = PdfFileWriter()

    # appending pdfs one by one
    for pdf in pdfs:
        # Show which file is being processed
        print(pdf)
        # Add all pages of this PDF to the end of the merged document
        pdfMerger.append(pdf)
        # Old approach using PdfFileReader/PdfFileWriter, kept for reference:
        #with open(pdf, 'rb') as f:
#        pdfReader = PdfFileReader(f)
#        print(pdfReader.numPages)
#        for pageNum in range(pdfReader.numPages):
#            pageObj = pdfReader.getPage(pageNum)
#            pdfWriter.addPage(pageObj)

    # writing combined pdf to output pdf file
    pdfOutputfile = open(output,'wb')
    pdfMerger.write(pdfOutputfile)
    #pdfWriter.write(pdfOutputfile)
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
