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
# document: https://pythonhosted.org/PyPDF2/
def pdf_merger(fname, newSize, pdf, output, fill, rotate):
    print("Merge PDF...")
    numPages = len(pdf.pages)
    pageWidth = math.ceil(pdf.pages[0].mediabox.width)
    pageHeight = math.ceil(pdf.pages[0].mediabox.height)
    pageDiagonal = math.sqrt(pageWidth**2 + pageHeight**2)
    print('pageWidth: {}, pageHeight: {}, pageDiagonal: {}'.format(pageWidth,pageHeight,pageDiagonal))

    numNewPages = 1 
    if (newSize == 'A4'):
        newWidth = 595
        newHeight = 842
        newDiagonal = 1031
        
    else:
        newSize = 'A3'# A3
        newWidth = 842
        newHeight = 1190
        newDiagonal = 1457

    print('newWidth: {}, newHeight: {}, newDiagonal: {}'.format(newWidth,newHeight,newDiagonal))
    print('........................................')
    print('Numer of pages to merge: {}'.format(numPages))
    print('Input file: {}.pdf, size: {}'.format(fname,newSize))

    # Finn ut hvor mange sider du skal fylle
    if (round(pageDiagonal/newDiagonal,1) == 1.0):
        if (newSize == 'A4'):
            print("Øker arkstørrelse til A3")
            newWidth = 842
            newHeight = 1190
            newDiagonal = 1457

        else:
            print("kan ikke sammenstille denne filen")
    if (round(pageDiagonal/newDiagonal,1) == 0.7):
        numNewPages = math.ceil(numPages/2)
        print("A5 -> A4 or A4 -> A3 , {} pages".format(numNewPages))
        if rotate:  # I tilfellet man har landscape
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
        print("A6 -> A3, {} pages".format(numNewPages))

    elif(round(pageDiagonal/newDiagonal,2) == 0.25):
        numNewPages = math.ceil(numPages/10)
        indices = create_matrix(6,4)
        rotate = 'portrait'
        print("A7 -> A4, {} pages".format(numNewPages))
    

    else: 
            print("Ukjent størrelse på ark")
    

    print('........................................')
    writer = PdfWriter()
        
    if (rotate == 'portrait'):
        translated_page = PageObject.create_blank_page(None, newWidth, newHeight) 
    else:
        translated_page = PageObject.create_blank_page(None, newHeight, newWidth) 
    i = 0
    if fill:
        if (numPages == 1):
            page = 0
            fullPage = True
            for i in range(len(indices)): # Arket blir fyllt opp
                print('{}_part'.format(page+1))
                sub_page = pdf.pages[page]
                sub_page.add_transformation(Transformation().translate(indices[i][0]*pageWidth , indices[i][1]*pageHeight))
                translated_page.merge_page(sub_page)
                #translated_page.mergeTranslatedPage(sub_page, indices[i][0]*pageHeight , indices[i][1]*pageWidth)
            writer.addPage(translated_page)
                
        else:
            print("else?")
    else:
        for page in range(numPages):
            print('{}_part'.format(page+1))
            sub_page = pdf.pages[page]
            sub_page.add_transformation(Transformation().translate(indices[i][0]*pageWidth , indices[i][1]*pageHeight))
            #translated_page.mergeTranslatedPage(sub_page, indices[i][0]*pageWidth , indices[i][1]*pageHeight)
            translated_page.merge_page(sub_page)
            #translated_page.mergeTranslatedPage(sub_page, indices[i][0]*pageHeight , indices[i][1]*pageWidth)
            i+=1
            fullPage = False
            if (i > len(indices)-1):
    #            print("New page")
                i = 0
                # create page to writer
                writer.add_page(translated_page)
                fullPage = True
                if (rotate == 'portrait'):
                    translated_page = PageObject.create_blank_page(None, newWidth, newHeight) 
                else:
                    translated_page = PageObject.create_blank_page(None, newHeight, newWidth) 
    if not fullPage:
        writer.add_page(translated_page)
    with open(output, 'wb') as f:
        writer.write(f)
    
    print('........................................')
    print('{} is written'.format(output))

def create_matrix(n,m):
    matrix = []
    for i in range(m,0,-1):
        for j in range(n):
            matrix.append([j,i-1])
    #print(matrix)
    return matrix

# pdf_splitter.py
def pdf_splitter(path):
    print("Split PDF...")

    fname = os.path.splitext(os.path.basename(path))[0]

    pdf = PdfeReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.pages[page])
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
#    parser.add_argument('--split', action='store_true', help="Split into separate files, and not merge")
    parser.add_argument('--open', action='store_true', default=False,
                        help='Open PDF after merging')
    args = parser.parse_args()
    pdf = PdfReader(args.input)
    fname = os.path.splitext(os.path.basename(args.input))[0]
    if not args.size:
        args.size = "A4"
    if not args.out:
        args.out = '{}_out.pdf'.format(fname)
#    if args.split:
#        pdf_splitter(args.input)
#    else:
    pdf_merger(fname, args.size, pdf, args.out,args.fill,args.rotate)
 
    if args.open: # and not args.split:
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", args.out])
        else:
            subprocess.call(["evince", args.out])

if __name__ == '__main__':
   main() 
