#!/usr/bin/env python
"""Merge pdfs to one page
Script that merges all pages in one pdf file to one page

Supported conversions:
- 2 * A5 -> A4 (landscape)
- 2 * A4 -> A3 (landscape)
- 4 * A6 -> A4 (2x2 grid)
- 4 * A5 -> A3 (2x2 grid)
- 8 * A7 -> A4 (4x2 grid)
- 8 * A6 -> A3 (4x2 grid)
- 16 * A8 -> A4 (4x4 grid)
- 16 * A7 -> A3 (4x4 grid)
- 32 * A8 -> A3 (8x4 grid)

The pages in the input file must have the same size (A4, A5, A6, A7, or A8)
If input file has only one page you can fill the page with the -f (--fill) argument
You can override paper size with -s (--size) argument

"""
from typing import List
from PyPDF2 import PdfReader, PdfWriter, Transformation
from PyPDF2 import PageObject
import os
import math
import argparse
import subprocess
import sys

# Paper size constants (width, height in points)
PAPER_SIZES = {
    'A3': {'width': 842, 'height': 1190},
    'A4': {'width': 595, 'height': 842},
}

def get_diagonal(width: int, height: int) -> float:
    """Calculate diagonal length from width and height."""
    return math.sqrt(width**2 + height**2)

def pdf_merger(fname: str, new_size: str, pdf: PdfReader, output: str, fill: bool, force_portrait: bool) -> None:
    print("Merge PDF...")
    num_pages = len(pdf.pages)

    # Validate PDF has pages
    if num_pages == 0:
        raise ValueError("PDF file has no pages")

    # Get first page dimensions (use round instead of ceil to avoid overflow)
    page_width = round(pdf.pages[0].mediabox.width)
    page_height = round(pdf.pages[0].mediabox.height)

    # Validate all pages have the same dimensions
    for i, page in enumerate(pdf.pages):
        width = round(page.mediabox.width)
        height = round(page.mediabox.height)
        if width != page_width or height != page_height:
            raise ValueError(f"Page {i+1} has different dimensions ({width}x{height}) than first page ({page_width}x{page_height})")

    page_diagonal = math.sqrt(page_width**2 + page_height**2)
    print('pageWidth: {}, pageHeight: {}, page_diagonal: {}'.format(page_width, page_height, page_diagonal))

    num_new_pages = 1
    if new_size == 'A4':
        new_width = PAPER_SIZES['A4']['width']
        new_height = PAPER_SIZES['A4']['height']
    else:
        new_size = 'A3'
        new_width = PAPER_SIZES['A3']['width']
        new_height = PAPER_SIZES['A3']['height']

    new_diagonal = get_diagonal(new_width, new_height)

    print('new_width: {}, new_height: {}, new_diagonal: {}'.format(new_width,new_height,new_diagonal))
    print('........................................')
    print('Number of pages to merge: {}'.format(num_pages))
    print('Input file: {}.pdf, size: {}'.format(fname,new_size))

    if (round(page_diagonal/new_diagonal,1) == 1.0):
        if (new_size == 'A4'):
            print("Increasing paper size to A3")
            new_width = PAPER_SIZES['A3']['width']
            new_height = PAPER_SIZES['A3']['height']
            new_diagonal = get_diagonal(new_width, new_height)
        else:
            print("Cannot merge this file")
    # Ratio 0.7 ≈ 1/√2: One step smaller (A5→A4, A4→A3)
    if (round(page_diagonal/new_diagonal,1) == 0.7):
        num_new_pages = math.ceil(num_pages/2)
        print("A5 -> A4 or A4 -> A3 , {} pages".format(num_new_pages))
        if force_portrait:
            indices = create_matrix(1,2)
            orientation = 'portrait'
        else:
            indices = create_matrix(2,1)
            orientation = 'landscape'

    # Ratio 0.5 ≈ (1/√2)²: Two steps smaller (A6→A4, A5→A3)
    elif(round(page_diagonal/new_diagonal,1) == 0.5):
        num_new_pages = math.ceil(num_pages/4)
        indices = create_matrix(2,2)
        print("A6 -> A4 or A5 -> A3, {} pages".format(num_new_pages))
        orientation = 'portrait'

    # Ratio 0.35 ≈ (1/√2)³: Three steps smaller (A7→A4, A6→A3)
    elif(round(page_diagonal/new_diagonal,2) == 0.35):
        num_new_pages = math.ceil(num_pages/8)
        indices = create_matrix(4,2)
        orientation = 'landscape'
        if new_size == 'A4':
            print("A7 -> A4, {} pages".format(num_new_pages))
        else:
            print("A6 -> A3, {} pages".format(num_new_pages))

    # Ratio 0.25 ≈ (1/√2)⁴: Four steps smaller (A8→A4, A7→A3)
    elif(round(page_diagonal/new_diagonal,2) == 0.25):
        num_new_pages = math.ceil(num_pages/16)
        indices = create_matrix(4,4)
        orientation = 'portrait'
        if new_size == 'A3':
            print("A7 -> A3, {} pages".format(num_new_pages))
        else:
            print("A8 -> A4, {} pages".format(num_new_pages))

    # Ratio 0.18 ≈ (1/√2)⁵: Five steps smaller (A8→A3)
    elif(round(page_diagonal/new_diagonal,2) == 0.18):
        num_new_pages = math.ceil(num_pages/32)
        indices = create_matrix(8,4)
        orientation = 'landscape'
        print("A8 -> A3, {} pages".format(num_new_pages))

    else:
        print(f"Unknown paper size: diagonal ratio {round(page_diagonal/new_diagonal,2)}")
        raise ValueError(f"Unsupported page size conversion. Input diagonal: {page_diagonal:.2f}, Output diagonal: {new_diagonal:.2f}")


    print('........................................')
    writer = PdfWriter()

    if (orientation == 'portrait'):
        translated_page = PageObject.create_blank_page(None, new_width, new_height)
    else:
        translated_page = PageObject.create_blank_page(None, new_height, new_width) 
    i = 0
    if fill and num_pages == 1:
        # Fill mode: duplicate single page to fill output page
        page = 0
        full_page = True
        for i in range(len(indices)):
            print('{}_part'.format(page+1))
            # Use mergeTranslatedPage to avoid issues with deepcopy
            x_offset = indices[i][0] * page_width
            y_offset = indices[i][1] * page_height
            translated_page.mergeTranslatedPage(pdf.pages[page], x_offset, y_offset)
        writer.add_page(translated_page)

    else:
        # Normal mode: merge pages sequentially
        if fill and num_pages > 1:
            print("Warning: Fill option only works with single-page PDFs. Processing normally.")

        for page in range(num_pages):
            print('{}_part'.format(page+1))
            # Use mergeTranslatedPage for proper positioning
            x_offset = indices[i][0] * page_width
            y_offset = indices[i][1] * page_height
            translated_page.mergeTranslatedPage(pdf.pages[page], x_offset, y_offset)
            i+=1
            full_page = False
            if (i > len(indices)-1):
                i = 0
                writer.add_page(translated_page)
                full_page = True
                if (orientation == 'portrait'):
                    translated_page = PageObject.create_blank_page(None, new_width, new_height)
                else:
                    translated_page = PageObject.create_blank_page(None, new_height, new_width)
        if not full_page:
            writer.add_page(translated_page)

    try:
        with open(output, 'wb') as f:
            writer.write(f)
    except IOError as e:
        print(f"Error writing output file '{output}': {e}")
        raise

    print('........................................')
    print('{} is written'.format(output))

def create_matrix(n: int, m: int) -> List[List[int]]:
    """Create a position matrix for arranging pages in an n×m grid.

    Pages are arranged from top to bottom, left to right.
    Returns list of [x, y] coordinates where x is column (0 to n-1)
    and y is row (0 to m-1), starting from top-left.
    """
    matrix = []
    for i in range(m, 0, -1):
        for j in range(n):
            matrix.append([j, i-1])
    return matrix

def main() -> None:
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
        pdf_merger(fname, args.size, pdf, args.out, args.fill, args.rotate)
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
