"""Append PDF files to one PDF file

Merge all given files into one PDF file.
Default filename is merge_file.pdf

Examples:
  python append_pdf_one_by_one.py file1.pdf file2.pdf file3.pdf
  python append_pdf_one_by_one.py *.pdf -o combined.pdf
  python append_pdf_one_by_one.py doc1.pdf doc2.pdf --open
"""
#!/usr/bin/env python
from PyPDF2 import PdfMerger, PdfReader
import argparse
import os
import sys
import subprocess


def pdf_merge(pdfs, output):
    """Merge multiple PDF files into one output file.

    Args:
        pdfs: List of PDF file paths to merge
        output: Output file path for merged PDF

    Raises:
        FileNotFoundError: If any input file doesn't exist
        ValueError: If input list is empty
    """
    if not pdfs:
        raise ValueError("No input files provided")

    print(f"Merging {len(pdfs)} PDF files...")

    pdf_merger = PdfMerger()
    total_pages = 0

    for i, pdf in enumerate(pdfs, 1):
        pdf_reader = PdfReader(pdf)
        num_pages = len(pdf_reader.pages)
        total_pages += num_pages
        print(f"  [{i}/{len(pdfs)}] Adding: {pdf} ({num_pages} pages)")
        pdf_merger.append(pdf)

    print(f"\nWriting output file...")
    with open(output, 'wb') as output_file:
        pdf_merger.write(output_file)

    print(f"Total pages merged: {total_pages}")

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='PDF files to merge', nargs='*')
    parser.add_argument('-o', '--output', default='merge_file.pdf',
                        help='Output PDF file (default: merge_file.pdf)')
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open PDF after merging')
    args = parser.parse_args()

    # Validate input
    if not args.input:
        print("Error: No input files provided")
        print("\nUsage: python append_pdf_one_by_one.py file1.pdf file2.pdf [file3.pdf ...]")
        sys.exit(1)

    # Validate all input files exist and are readable PDFs
    for pdf_file in args.input:
        if not os.path.isfile(pdf_file):
            print(f"Error: File not found: '{pdf_file}'")
            sys.exit(1)

        # Verify file is a valid PDF
        try:
            PdfReader(pdf_file)
        except Exception as e:
            print(f"Error: '{pdf_file}' is not a valid PDF: {e}")
            sys.exit(1)

    try:
        pdf_merge(args.input, args.output)
        print('........................................')
        print('{} successfully created'.format(args.output))
    except ValueError as e:
        print(f"Error: {e}")
        # Clean up partial output file if it exists
        if os.path.exists(args.output):
            os.remove(args.output)
        sys.exit(1)
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        # Clean up partial output file if it exists
        if os.path.exists(args.output):
            print(f"Cleaning up partial output file...")
            os.remove(args.output)
        sys.exit(1)

    if args.open:
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", args.output])
        else:
            subprocess.call(["evince", args.output])


if __name__ == "__main__":
    main()
