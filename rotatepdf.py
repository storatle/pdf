#!/usr/bin/env python3
"""Rotate pages in a PDF file.

Rotate all pages in a PDF file by a specified angle (90, 180, or 270 degrees).
Default rotation is 90 degrees clockwise.

Examples:
    python rotatepdf.py input.pdf                      # Rotate 90° clockwise
    python rotatepdf.py input.pdf -r 180               # Rotate 180°
    python rotatepdf.py input.pdf -o output.pdf        # Specify output file
    python rotatepdf.py input.pdf -r 270 --open        # Rotate 270° and open result
    python rotatepdf.py input.pdf -y                   # Skip overwrite confirmation
"""

import argparse
import os
import subprocess
import sys

from PyPDF2 import PdfReader, PdfWriter


def rotate_pdf(input_file, output_file, angle=90):
    """Rotate all pages in a PDF file.

    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        angle: Rotation angle in degrees (90, 180, 270)

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is not a valid PDF
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

    print(f'Rotating {num_pages} pages by {angle}° clockwise...')

    pdf_writer = PdfWriter()

    # Rotate all pages
    for i, page in enumerate(pdf_reader.pages, 1):
        page.rotate(angle)
        pdf_writer.add_page(page)
        print(f'  [{i}/{num_pages}] Rotated page {i}')

    # Write output file
    with open(output_file, 'wb') as output:
        pdf_writer.write(output)

    print(f'Done. Output saved to: {output_file}')


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Input PDF file to rotate')
    parser.add_argument('-o', '--out', help='Output PDF file (default: input_rotated.pdf)')
    parser.add_argument('-r', '--rotation', type=int, choices=[90, 180, 270],
                        default=90, help='Rotation angle in degrees: 90, 180, or 270 (default: 90)')
    parser.add_argument('-y', '--yes', action='store_true', default=False,
                        help='Skip confirmation prompt if output file exists')
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open PDF after rotating')
    args = parser.parse_args()

    # Set output file
    if args.out:
        output_file = args.out
    else:
        # Default: add _rotated before extension
        base_name, extension = os.path.splitext(args.input)
        output_file = f'{base_name}_rotated{extension}'

    # Check if output file exists and confirm overwrite
    if os.path.exists(output_file) and not args.yes:
        print(f'Warning: Output file already exists: {output_file}')
        response = input('Overwrite? [y/N]: ').strip().lower()
        if response not in ['y', 'yes']:
            print('Operation cancelled.')
            sys.exit(0)

    # Rotate PDF with error handling
    try:
        rotate_pdf(args.input, output_file, angle=args.rotation)
    except FileNotFoundError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error rotating PDF: {e}')
        sys.exit(1)

    # Open the output file if requested
    if args.open:
        if sys.platform == 'win32':
            subprocess.call(['explorer.exe', output_file])
        else:
            subprocess.call(['evince', output_file])


if __name__ == '__main__':
    main()
