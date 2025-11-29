"""Merge pdfs to one page
Script that merges all pages in one pdf file to one page
4 * A6 -> A4
2 * A5 -> A4
8 * A6 -> A3
4 * A5 -> A3
2 * A4 -> A3

The pages in the input file must have same size and in A6, A5 or A4 format
If input file has only one page you can fill the page with the -f (--fill) argument
You can override paper size with -s (--size) argument

"""

#!/usr/bin/env python
from PyPDF2 import PdfReader, PdfWriter, Transformation
from PyPDF2 import PageObject
import os
import math
import argparse
import subprocess
import sys

# Paper size constants (width, height, diagonal)
PAPER_SIZES = {
    'A3': {'width': 842, 'height': 1190, 'diagonal': 1457},
    'A4': {'width': 595, 'height': 842, 'diagonal': 1031},
}

def pdf_merger(fname, newSize, pdf, output, fill, rotate):
    print("Merge PDF...")
    numPages = len(pdf.pages)

    # Validate PDF has pages
    if numPages == 0:
        raise ValueError("PDF file has no pages")

    # Get first page dimensions (use round instead of ceil to avoid overflow)
    pageWidth = round(pdf.pages[0].mediabox.width)
    pageHeight = round(pdf.pages[0].mediabox.height)

    # Validate all pages have the same dimensions
    for i, page in enumerate(pdf.pages):
        width = round(page.mediabox.width)
        height = round(page.mediabox.height)
        if width != pageWidth or height != pageHeight:
            raise ValueError(f"Page {i+1} has different dimensions ({width}x{height}) than first page ({pageWidth}x{pageHeight})")

    pageDiagonal = math.sqrt(pageWidth**2 + pageHeight**2)
    print('pageWidth: {}, pageHeight: {}, pageDiagonal: {}'.format(pageWidth,pageHeight,pageDiagonal))

    numNewPages = 1
    if newSize == 'A4':
        newWidth = PAPER_SIZES['A4']['width']
        newHeight = PAPER_SIZES['A4']['height']
        newDiagonal = PAPER_SIZES['A4']['diagonal']
    else:
        newSize = 'A3'
        newWidth = PAPER_SIZES['A3']['width']
        newHeight = PAPER_SIZES['A3']['height']
        newDiagonal = PAPER_SIZES['A3']['diagonal']

    print('newWidth: {}, newHeight: {}, newDiagonal: {}'.format(newWidth,newHeight,newDiagonal))
    print('........................................')
    print('Number of pages to merge: {}'.format(numPages))
    print('Input file: {}.pdf, size: {}'.format(fname,newSize))

    if (round(pageDiagonal/newDiagonal,1) == 1.0):
        if (newSize == 'A4'):
            print("Increasing paper size to A3")
            newWidth = PAPER_SIZES['A3']['width']
            newHeight = PAPER_SIZES['A3']['height']
            newDiagonal = PAPER_SIZES['A3']['diagonal']
        else:
            print("Cannot merge this file")
    if (round(pageDiagonal/newDiagonal,1) == 0.7):
        numNewPages = math.ceil(numPages/2)
        print("A5 -> A4 or A4 -> A3 , {} pages".format(numNewPages))
        if rotate:
            indices = create_matrix(1,2)
            rotate = 'portrait'
        else:
            indices = create_matrix(2,1)
            rotate = 'landscape'

    elif(round(pageDiagonal/newDiagonal,1) == 0.5):
        numNewPages = math.ceil(numPages/4)
        indices = create_matrix(2,2)
        print("A6 -> A4 or A5 -> A3, {} pages".format(numNewPages))
        rotate = 'portrait'

    elif(round(pageDiagonal/newDiagonal,2) == 0.35):
        numNewPages = math.ceil(numPages/8)
        indices = create_matrix(4,2)
        rotate = 'landscape'
        if newSize == 'A4':
            print("A7 -> A4, {} pages".format(numNewPages))
        else:
            print("A6 -> A3, {} pages".format(numNewPages))

    elif(round(pageDiagonal/newDiagonal,2) == 0.25):
        numNewPages = math.ceil(numPages/16)
        indices = create_matrix(4,4)
        rotate = 'portrait'
        if newSize == 'A3':
            print("A7 -> A3, {} pages".format(numNewPages))
        else:
            print("A8 -> A4, {} pages".format(numNewPages))

    elif(round(pageDiagonal/newDiagonal,2) == 0.18):
        numNewPages = math.ceil(numPages/32)
        indices = create_matrix(8,4)
        rotate = 'landscape'
        print("A8 -> A3, {} pages".format(numNewPages))

    else:
            print("Unknown paper size")
    

    print('........................................')
    writer = PdfWriter()
        
    if (rotate == 'portrait'):
        translated_page = PageObject.create_blank_page(None, newWidth, newHeight) 
    else:
        translated_page = PageObject.create_blank_page(None, newHeight, newWidth) 
    i = 0
    if fill and numPages == 1:
        # Fill mode: duplicate single page to fill output page
        page = 0
        fullPage = True
        for i in range(len(indices)):
            print('{}_part'.format(page+1))
            # Use mergeTranslatedPage to avoid issues with deepcopy
            x_offset = indices[i][0] * pageWidth
            y_offset = indices[i][1] * pageHeight
            translated_page.mergeTranslatedPage(pdf.pages[page], x_offset, y_offset)
        writer.add_page(translated_page)

    else:
        # Normal mode: merge pages sequentially
        if fill and numPages > 1:
            print("Warning: Fill option only works with single-page PDFs. Processing normally.")

        for page in range(numPages):
            print('{}_part'.format(page+1))
            # Use mergeTranslatedPage for proper positioning
            x_offset = indices[i][0] * pageWidth
            y_offset = indices[i][1] * pageHeight
            translated_page.mergeTranslatedPage(pdf.pages[page], x_offset, y_offset)
            i+=1
            fullPage = False
            if (i > len(indices)-1):
                i = 0
                writer.add_page(translated_page)
                fullPage = True
                if (rotate == 'portrait'):
                    translated_page = PageObject.create_blank_page(None, newWidth, newHeight)
                else:
                    translated_page = PageObject.create_blank_page(None, newHeight, newWidth)
        if not fullPage:
            writer.add_page(translated_page)

    try:
        with open(output, 'wb') as f:
            writer.write(f)
    except IOError as e:
        print(f"Error writing output file '{output}': {e}")
        raise

    print('........................................')
    print('{} is written'.format(output))

def create_matrix(n,m):
    matrix = []
    for i in range(m,0,-1):
        for j in range(n):
            matrix.append([j,i-1])
    return matrix

def pdf_splitter(path):
    print("Split PDF...")

    fname = os.path.splitext(os.path.basename(path))[0]

    pdf = PdfReader(path)
    for page in range(len(pdf.pages)):
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf.pages[page])
        output_filename = '{}_page_{}.pdf'.format(
            fname, page+1)

        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename))

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('input', help='Relative or absolute path of the input PDF file')
    parser.add_argument('-o', '--out', help='Relative or absolute path of the output PDF file')
    parser.add_argument('-s', '--size', help='size of out paper A4 or A3')
    parser.add_argument('-f', '--fill', action='store_true', default=False, help="Fill page if only one page in input file")
    parser.add_argument('-r', '--rotate', action='store_true', default=False, help="Set orientation of original file.")
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open PDF after merging')
    args = parser.parse_args()

    try:
        pdf = PdfReader(args.input)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        sys.exit(1)

    fname = os.path.splitext(os.path.basename(args.input))[0]
    if not args.size:
        args.size = "A4"
    if not args.out:
        args.out = '{}_out.pdf'.format(fname)

    try:
        pdf_merger(fname, args.size, pdf, args.out,args.fill,args.rotate)
    except Exception as e:
        print(f"Error merging PDF: {e}")
        sys.exit(1)

    if args.open:
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", args.out])
        else:
            subprocess.call(["evince", args.out])

if __name__ == '__main__':
   main() 
