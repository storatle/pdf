# PDF Merger - merge_pdf_to_one_page.py

A Python script that merges multiple small PDF pages onto larger paper formats, optimizing paper usage by arranging pages in grids.

## Overview

This tool automatically detects the input PDF page size and arranges multiple pages onto a single larger sheet. Common use cases include:
- Merging 4 A6 pages into one A4 page (2×2 grid)
- Merging 2 A5 pages into one A4 page (side-by-side)
- Merging 16 A8 pages into one A4 page (4×4 grid)

## Requirements

```bash
pip install PyPDF2
```

## Usage

### Basic Usage

```bash
python merge_pdf_to_one_page.py input.pdf
```

This will:
- Automatically detect the page size
- Determine the optimal output format (A4 or A3)
- Create `input_out.pdf` with merged pages

### Command Line Options

```bash
python merge_pdf_to_one_page.py input.pdf [OPTIONS]
```

**Options:**
- `-o, --out OUTPUT`: Specify output file path (default: `input_out.pdf`)
- `-s, --size SIZE`: Override output paper size (`A4` or `A3`)
- `-f, --fill`: Fill page by duplicating a single-page PDF to all grid positions
- `-r, --rotate`: Change orientation (portrait/landscape)
- `--open`: Automatically open the PDF after merging (uses `evince` on Linux)

### Examples

**Merge 4 A6 pages to A4:**
```bash
python merge_pdf_to_one_page.py document.pdf
```

**Fill A4 page with one A6 page (duplicate 4 times):**
```bash
python merge_pdf_to_one_page.py single_page.pdf -f
```

**Force A3 output:**
```bash
python merge_pdf_to_one_page.py input.pdf -s A3
```

**Custom output file and auto-open:**
```bash
python merge_pdf_to_one_page.py input.pdf -o merged.pdf --open
```

## Supported Conversions

The script automatically detects the input page size and selects the appropriate conversion:

| Input Size | Output Size | Grid Layout | Pages per Sheet | Orientation |
|------------|-------------|-------------|-----------------|-------------|
| A5 | A4 | 2×1 | 2 | Landscape |
| A4 | A3 | 2×1 | 2 | Landscape |
| A6 | A4 | 2×2 | 4 | Portrait |
| A5 | A3 | 2×2 | 4 | Portrait |
| A7 | A4 | 4×2 | 8 | Landscape |
| A6 | A3 | 4×2 | 8 | Landscape |
| A8 | A4 | 4×4 | 16 | Portrait |
| A7 | A3 | 4×4 | 16 | Portrait |
| A8 | A3 | 8×4 | 32 | Landscape |

### Conversion Details

**Small conversions (2 pages):**
- A5 → A4: Two A5 pages side-by-side on landscape A4
- A4 → A3: Two A4 pages side-by-side on landscape A3

**Medium conversions (4 pages):**
- A6 → A4: Four A6 pages in 2×2 grid on portrait A4
- A5 → A3: Four A5 pages in 2×2 grid on portrait A3

**Large conversions (8 pages):**
- A7 → A4: Eight A7 pages in 4×2 grid on landscape A4
- A6 → A3: Eight A6 pages in 4×2 grid on landscape A3

**Very large conversions (16+ pages):**
- A8 → A4: Sixteen A8 pages in 4×4 grid on portrait A4
- A7 → A3: Sixteen A7 pages in 4×4 grid on portrait A3
- A8 → A3: Thirty-two A8 pages in 8×4 grid on landscape A3

## Fill Mode (`-f` flag)

The fill mode is designed for single-page PDFs. It duplicates the page to fill all available positions on the output sheet.

**Use cases:**
- Creating multiple copies of a label or sticker on one sheet
- Duplicating a small design across a larger page
- Testing print layouts

**Example:**
```bash
# Single A6 page → Fill A4 with 4 copies
python merge_pdf_to_one_page.py label.pdf -f

# Single A8 page → Fill A4 with 16 copies
python merge_pdf_to_one_page.py small_sticker.pdf -s A4 -f
```

**Note:** Fill mode only works with single-page PDFs. If you provide a multi-page PDF with `-f`, the script will show a warning and process it normally.

## How It Works

1. **Page Detection**: Reads the first page dimensions and validates all pages match
2. **Ratio Calculation**: Calculates diagonal ratio between input and output sizes
3. **Grid Selection**: Chooses appropriate grid layout based on the ratio
4. **Positioning**: Places pages from top-left, filling left-to-right, top-to-bottom
5. **Output**: Writes merged pages to the output PDF

## Input Requirements

- **Consistent page sizes**: All pages in the input PDF must have the same dimensions
- **Supported sizes**: A4, A5, A6, A7, or A8 (standard or near-standard dimensions)
- **Valid PDF**: File must be readable by PyPDF2

## Error Handling

The script will report errors for:
- File not found
- Invalid PDF format
- Inconsistent page dimensions within the PDF
- Unsupported page size ratios

## Notes

- Pages are positioned starting from the **top-left corner**
- The script uses the `mergeTranslatedPage()` method for reliable page positioning
- Dimensions are rounded (not ceiling) to prevent overflow issues
- The `-r` (rotate) flag can adjust orientation for specific conversions

## Technical Details

**Paper Size Constants:**
- A3: 842 × 1190 points
- A4: 595 × 842 points

Standard A-series dimensions (mm):
- A3: 297 × 420
- A4: 210 × 297
- A5: 148 × 210
- A6: 105 × 148
- A7: 74 × 105
- A8: 52 × 74

## Example Workflow

```bash
# You have a PDF with 8 A6 pages and want to print on A4 paper
python merge_pdf_to_one_page.py my_document.pdf

# Output:
# Merge PDF...
# pageWidth: 298, pageHeight: 420, pageDiagonal: 514.98
# newWidth: 595, newHeight: 842, newDiagonal: 1031
# ........................................
# Number of pages to merge: 8
# Input file: my_document.pdf, size: A4
# A6 -> A4 or A5 -> A3, 2 pages
# ........................................
# 1_part
# 2_part
# 3_part
# 4_part
# 5_part
# 6_part
# 7_part
# 8_part
# ........................................
# my_document_out.pdf is written

# Result: 2 A4 pages, each containing 4 A6 pages in a 2×2 grid
```

## License

This script is provided as-is for PDF manipulation tasks.
