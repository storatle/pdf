#!/usr/bin/env python3
"""Extract text from a PDF file.

Extract text content from a PDF file and save it to a text file.
Default output filename is the same as input with .txt extension.

Note: This tool extracts embedded text from PDFs. Scanned documents
(images without text layer) will produce empty or minimal output.
For scanned PDFs, consider using OCR tools like Tesseract.

Examples:
    python parse_pdf_to_text.py input.pdf                    # Extract to input.txt
    python parse_pdf_to_text.py document.pdf -o output.txt   # Specify output file
    python parse_pdf_to_text.py file.pdf -v                  # Verbose output
    python parse_pdf_to_text.py scan.pdf -y --open           # Skip confirmation and open
"""

import argparse
import os
import subprocess
import sys

from PyPDF2 import PdfReader


def extract_text_from_pdf(input_file, output_file, verbose=False):
    """Extract text from a PDF file and save to text file.

    Args:
        input_file: Path to input PDF file
        output_file: Path to output text file
        verbose: If True, show progress for each page

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is not a valid PDF

    Returns:
        int: Total number of characters extracted
    """
    # Validate input file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f'Input file not found: \'{input_file}\'')

    # Read and validate PDF
    try:
        pdf_reader = PdfReader(input_file)
    except Exception as e:
        raise ValueError(f'Error reading PDF file: {e}')

    num_pages = len(pdf_reader.pages)
    if num_pages == 0:
        raise ValueError('PDF file has no pages')

    print(f'Extracting text from {num_pages} pages...')

    # Extract text page by page, writing incrementally
    text_parts = []
    total_chars = 0

    for i, page in enumerate(pdf_reader.pages, 1):
        if verbose:
            print(f'  [{i}/{num_pages}] Processing page {i}...')

        page_text = page.extract_text()
        text_parts.append(page_text)
        total_chars += len(page_text)

    # Combine all text
    full_text = '\n'.join(text_parts)

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write(full_text)

    # Check if extraction was successful
    if total_chars == 0:
        print('\nWarning: No text could be extracted from the PDF.')
        print('This may be a scanned document (image-based PDF) without a text layer.')
        print('For scanned documents, consider using OCR tools like Tesseract or Adobe Acrobat.')
    elif total_chars < 100:
        print(f'\nWarning: Only {total_chars} characters extracted. PDF may be mostly images.')

    print(f'Done. Extracted {total_chars:,} characters to: {output_file}')

    return total_chars


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Input PDF file to extract text from')
    parser.add_argument('-o', '--out', help='Output text file (default: input.txt)')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Show progress for each page')
    parser.add_argument('-y', '--yes', action='store_true', default=False,
                        help='Skip confirmation prompt if output file exists')
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open text file after extraction')
    args = parser.parse_args()

    # Set output file
    if args.out:
        output_file = args.out
    else:
        # Default: same name as input with .txt extension
        base_name = os.path.splitext(args.input)[0]
        output_file = f'{base_name}.txt'

    # Check if output file exists and confirm overwrite
    if os.path.exists(output_file) and not args.yes:
        print(f'Warning: Output file already exists: {output_file}')
        response = input('Overwrite? [y/N]: ').strip().lower()
        if response not in ['y', 'yes']:
            print('Operation cancelled.')
            sys.exit(0)

    # Extract text with error handling
    try:
        extract_text_from_pdf(args.input, output_file, verbose=args.verbose)
    except FileNotFoundError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error extracting text: {e}')
        sys.exit(1)

    # Open the output file if requested
    if args.open:
        if sys.platform == 'win32':
            subprocess.call(['notepad.exe', output_file])
        else:
            # Try common text editors
            for editor in ['gedit', 'kate', 'nano', 'vim']:
                if subprocess.call(['which', editor], stdout=subprocess.DEVNULL) == 0:
                    subprocess.call([editor, output_file])
                    break


if __name__ == '__main__':
    main()
