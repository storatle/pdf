#!/usr/bin/env python
"""Split PDF files into separate files.

Split modes:
  -p 0 (default): Split into individual single-page PDFs
  -p N: Split into two files at page N (pages 1-N and N+1-end)

Examples:
  python split_pdf.py input.pdf              # Split every page
  python split_pdf.py input.pdf -p 5         # Split at page 5
  python split_pdf.py input.pdf -p 3 --open  # Split at page 3 and open result
"""
from PyPDF2 import PdfReader, PdfWriter
import os
import argparse
import subprocess
import sys


def pdf_splitter(path, split_page):
    print("Split PDF...")
    fname = os.path.splitext(os.path.basename(path))[0]
    pdf = PdfReader(path)
    num_pages = len(pdf.pages)

    # Validate split_page parameter
    if split_page < 0:
        raise ValueError("Split page must be 0 or positive")

    # Check if PDF has enough pages to split
    if split_page == 0 and num_pages == 1:
        print(f"Warning: PDF has only 1 page. Creating single-page output file.")
    elif split_page > 0:
        # For two-file split mode, need at least 2 pages
        if num_pages == 1:
            raise ValueError(f"Cannot split a 1-page PDF at page {split_page}. Use -p 0 to extract the single page.")
        # Ensure split point creates non-empty files
        if split_page >= num_pages:
            raise ValueError(f"Cannot split at page {split_page}. PDF only has {num_pages} pages. Use a number between 1 and {num_pages-1}.")

    print(f"PDF has {num_pages} pages")

    if split_page == 0:
        # Split at every page
        print(f"Splitting into {num_pages} individual files...")
        for page in range(len(pdf.pages)):
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf.pages[page])
            output_filename = '{}_page_{}.pdf'.format(fname, page+1)

            with open(output_filename, 'wb') as out:
                pdf_writer.write(out)
            print('Created: {}'.format(output_filename))
    else:
        # Split into two files at specified page
        print(f"Splitting into 2 files at page {split_page}...")
        print(f"  File 1: pages 1-{split_page} ({split_page} pages)")
        print(f"  File 2: pages {split_page+1}-{num_pages} ({num_pages-split_page} pages)")

        pdf_writer = PdfWriter()
        for page in range(split_page):
            pdf_writer.add_page(pdf.pages[page])
        output_filename = '{}_page_{}.pdf'.format(fname, 1)
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename))

        pdf_writer = PdfWriter()
        for page in range(split_page, len(pdf.pages)):
            pdf_writer.add_page(pdf.pages[page])
        output_filename = '{}_page_{}.pdf'.format(fname, 2)
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename))


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Relative or absolute path of the input PDF file')
    parser.add_argument('-p', '--page', type=int, default=0, help='Split at page number (0 = split all pages, N = split at page N)')
    parser.add_argument('--open', action='store_true', default=False, help='Open first PDF after splitting')
    args = parser.parse_args()

    # Error handling for file operations
    try:
        pdf = PdfReader(args.input)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        sys.exit(1)

    fname = os.path.splitext(os.path.basename(args.input))[0]

    try:
        pdf_splitter(args.input, args.page)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error splitting PDF: {e}")
        sys.exit(1)
 
    if args.open:
        # Note: When splitting, multiple files are created
        # Only opens the first file in split mode
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", '{}_page_1.pdf'.format(fname)])
        else:
            subprocess.call(["evince", '{}_page_1.pdf'.format(fname)])

if __name__ == '__main__':
    main()
