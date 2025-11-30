# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a collection of Python utilities for PDF manipulation using PyPDF2. The primary tool is `merge_pdf_to_one_page.py`, which intelligently merges small PDF pages onto larger paper formats to optimize printing.

## Dependencies

All scripts require PyPDF2:
```bash
pip install PyPDF2
```

The `compress_pdf.py` script additionally requires Ghostscript to be installed and available on PATH.

## Core Scripts

### merge_pdf_to_one_page.py (Primary Tool)

The main utility for arranging multiple small PDF pages onto larger sheets. This is the most actively developed script in the repository.

**Architecture:**
- Uses diagonal ratio calculations to detect page size relationships (A-series paper follows 1/√2 ratio)
- Supports 9 different conversion patterns based on ratio detection (0.7, 0.5, 0.35, 0.25, 0.18)
- Creates position matrices using `create_matrix(n, m)` for grid-based page arrangement
- Uses `mergeTranslatedPage()` instead of deprecated methods for reliable positioning
- Rounds dimensions (not ceiling) to prevent overflow issues

**Key Functions:**
- `pdf_merger()`: Main merging logic, handles page validation and grid positioning
- `create_matrix(n, m)`: Generates coordinate lists for n×m grids, top-to-bottom, left-to-right
- `get_diagonal()`: Calculates diagonal for ratio-based size detection

**Usage:**
```bash
# Auto-detect and merge
python merge_pdf_to_one_page.py input.pdf

# Fill page with single-page PDF
python merge_pdf_to_one_page.py label.pdf -f

# Force output size
python merge_pdf_to_one_page.py input.pdf -s A3

# Auto-open after processing (uses evince on Linux)
python merge_pdf_to_one_page.py input.pdf --open
```

### Other Utilities

**append_pdf_one_by_one.py:**
- Concatenates multiple PDFs into a single file
- Uses `PdfMerger` for sequential appending
- Default output: `merge_file.pdf`

**compress_pdf.py:**
- Wrapper for Ghostscript PDF compression
- 5 compression levels (0=default, 1=prepress, 2=printer, 3=ebook, 4=screen)
- Detects Ghostscript executable across platforms
- Supports backup mode with `-b` flag

**split_pdf.py:**
- Splits PDFs either at every page or at a specific page number
- `-p 0`: Split into individual pages
- `-p N`: Split into two files at page N

**parse_pdf_to_text.py:**
- Extracts text from PDF to `.txt` file
- Uses deprecated PyPDF2 APIs (`PdfFileReader`, `getPage`, etc.)

**rotatepdf.py:**
- Rotates all pages 90° clockwise
- Outputs to `rotated.pdf`
- Also uses deprecated PyPDF2 APIs

## Code Patterns

### PyPDF2 API Usage

**Modern (merge_pdf_to_one_page.py, split_pdf.py, append_pdf_one_by_one.py):**
```python
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
pdf = PdfReader(path)
num_pages = len(pdf.pages)
page = pdf.pages[index]
writer.add_page(page)
```

**Deprecated (parse_pdf_to_text.py, rotatepdf.py):**
```python
from PyPDF2 import PdfFileReader, PdfFileWriter
pdf = PdfFileReader(path)
num_pages = pdf.numPages
page = pdf.getPage(index)
writer.addPage(page)
```

When modifying older scripts, update to modern PyPDF2 API.

### Platform-Specific File Opening

All scripts use this pattern for the `--open` flag:
```python
if sys.platform == "win32":
    subprocess.call(["explorer.exe", output_file])
else:
    subprocess.call(["evince", output_file])
```

## Testing

The `test/` directory contains sample PDFs for various paper sizes (A4-A8) and conversion scenarios. Test files follow naming pattern: `{size}_{variant}.pdf` and `{size}_out.pdf` for expected outputs.

## Development Notes

### merge_pdf_to_one_page.py Architecture Details

**Page Positioning Logic:**
- Pages are placed using `mergeTranslatedPage(page, x_offset, y_offset)`
- Offsets calculated as: `x_offset = column * page_width`, `y_offset = row * page_height`
- Position matrix creates coordinates from top-left, filling left-to-right, then top-to-bottom

**Ratio Detection:**
- Diagonal ratios determine conversion type (e.g., 0.7 = one step smaller in A-series)
- Rounded to 1 decimal (0.7, 0.5) or 2 decimals (0.35, 0.25, 0.18) depending on precision needed
- If ratio is 1.0 and output is A4, automatically upgrades to A3

**Fill Mode (`-f` flag):**
- Only works with single-page PDFs
- Duplicates the page to all grid positions
- Use case: creating multiple copies of labels/stickers on one sheet

**Orientation Logic:**
- Most conversions have fixed orientation based on optimal fit
- `-r` flag can override to force portrait on normally-landscape conversions
- Blank pages created with swapped dimensions for landscape: `PageObject.create_blank_page(None, height, width)`

### Common Development Patterns

**Error Handling:**
- Validate file existence before processing
- Check page dimension consistency (all pages must match in merge operations)
- Use try-except with sys.exit(1) for CLI scripts

**Output Naming:**
- Default pattern: `{input_basename}_out.pdf`
- Extract basename: `os.path.splitext(os.path.basename(path))[0]`

## Running Scripts

All main scripts are executable and follow this pattern:
```bash
python script_name.py input.pdf [OPTIONS]
```

Common options across scripts:
- `-o, --out`: Custom output path
- `--open`: Auto-open result after processing
