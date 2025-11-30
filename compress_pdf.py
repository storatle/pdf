"""
Simple python wrapper script to use Ghostscript function to compress PDF files.

Compression levels:
    0: default
    1: prepress
    2: printer (default)
    3: ebook
    4: screen

Dependency: Ghostscript must be installed and available on PATH.

Examples:
    python compress_pdf.py input.pdf                    # Compress with default level 2
    python compress_pdf.py input.pdf -c 4               # Maximum compression (screen quality)
    python compress_pdf.py input.pdf -o output.pdf      # Specify output file
    python compress_pdf.py input.pdf -b                 # Backup original before overwriting
"""
#!/usr/bin/env python3
# Author: Theeko74
# Contributor(s): skjerns
# Oct, 2021
# MIT license -- free to use as you want, cheers.

import argparse
import os
import subprocess
import shutil
import sys
import tempfile
from datetime import datetime

# Constants
BACKUP_SUFFIX = '_BACKUP.pdf'


def format_file_size(size_bytes):
    """Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        str: Formatted size string (e.g., "1.5MB", "345KB")
    """
    if size_bytes < 1024:
        return f'{size_bytes}B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f}KB'
    else:
        return f'{size_bytes / (1024 * 1024):.1f}MB'


def compress(input_file_path, output_file_path, power=0):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    # Validate input file exists
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError(f"Input file not found: '{input_file_path}'")

    # Validate file is a PDF (check extension and try to verify it's readable)
    if not input_file_path.lower().endswith('.pdf'):
        raise ValueError(f"Input file must have .pdf extension: '{input_file_path}'")

    # Try to verify it's actually a PDF by checking magic bytes
    try:
        with open(input_file_path, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                raise ValueError(f"File does not appear to be a valid PDF: '{input_file_path}'")
    except IOError as e:
        raise IOError(f"Cannot read input file: {e}")

    gs = get_ghostscript_path()
    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)

    # Execute Ghostscript compression
    return_code = subprocess.call([gs, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    f'-dPDFSETTINGS={quality[power]}',
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    f'-sOutputFile={output_file_path}',
                     input_file_path]
    )

    # Check if Ghostscript succeeded
    if return_code != 0:
        raise RuntimeError(f"Ghostscript compression failed with exit code {return_code}")

    # Verify output file was created
    if not os.path.isfile(output_file_path):
        raise RuntimeError(f"Output file '{output_file_path}' was not created")

    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)

    # Handle negative compression (file got larger)
    if ratio < 0:
        print(f'Warning: Compressed file is {abs(ratio):.0%} larger than original')
        print(f'Original size: {format_file_size(initial_size)}, Compressed size: {format_file_size(final_size)}')
    else:
        print(f'Compression by {ratio:.0%}.')
        print(f'Final file size is {format_file_size(final_size)}')

    print('Done.')


def get_ghostscript_path():
    """Find Ghostscript executable on the system PATH.

    Returns:
        str: Path to Ghostscript executable

    Raises:
        FileNotFoundError: If Ghostscript is not found
    """
    gs_names = ['gs', 'gswin32', 'gswin64']
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)

    raise FileNotFoundError(f"No Ghostscript executable was found on path ({'/'.join(gs_names)})")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Relative or absolute path of the input PDF file')
    parser.add_argument('-o', '--out', help='Relative or absolute path of the output PDF file')
    parser.add_argument('-c', '--compress', type=int, help='Compression level from 0 to 4')
    parser.add_argument('-b', '--backup', action='store_true', help='Backup the old PDF file')
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open PDF after compression')
    args = parser.parse_args()

    # Set default compression level
    if args.compress is None:
        args.compress = 2

    # Validate compression level
    if args.compress < 0 or args.compress > 4:
        print(f'Error: Compression level must be between 0 and 4 (received: {args.compress})')
        sys.exit(1)

    # Determine if we're replacing the original file
    replace_original = not args.out
    temp_file = None

    # Create temporary file for compression if replacing original
    if replace_original:
        # Use tempfile module for safe temporary file creation
        fd, temp_file = tempfile.mkstemp(suffix='.pdf', prefix='compress_')
        os.close(fd)  # Close file descriptor, we just need the path
        args.out = temp_file

    # Run compression with error handling and cleanup
    try:
        compress(args.input, args.out, power=args.compress)

        # Replace original file if temp file was used
        if replace_original:
            if args.backup:
                # Create backup with timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = os.path.splitext(args.input)[0]
                backup_path = f'{base_name}_BACKUP_{timestamp}.pdf'

                # Check if backup already exists (rare but possible)
                if os.path.exists(backup_path):
                    print(f'Warning: Backup file already exists: {backup_path}')
                    response = input('Overwrite? [y/N]: ').strip().lower()
                    if response != 'y':
                        print('Backup cancelled. Compressed file saved to temp location.')
                        print(f'Temp file: {temp_file}')
                        sys.exit(0)

                shutil.copyfile(args.input, backup_path)
                print(f'Backup created: {backup_path}')

            shutil.copyfile(args.out, args.input)

    except FileNotFoundError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except RuntimeError as e:
        print(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error during compression: {e}')
        sys.exit(1)
    finally:
        # Always clean up temp file if it was created
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                print(f'Warning: Could not remove temp file {temp_file}: {e}')

    # Open the final output file if requested
    if args.open:
        final_file = args.input if replace_original else args.out

        if sys.platform == 'win32':
            subprocess.call(['explorer.exe', final_file])
        else:
            subprocess.call(['evince', final_file])


if __name__ == '__main__':
    main()
