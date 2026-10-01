"""Parse text from a pdf file
The text will be placed in a text fiel with the same name as pdf file

"""
#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
from pypdf import PdfReader

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Relative or absolute path of the input PDF file')

    args = parser.parse_args()
    pdfreader = PdfReader(args.input)
    fname = os.path.splitext(os.path.basename(args.input))[0]
    x = len(pdfreader.pages)
    outputfile = open('{}.txt'.format(fname),'w',encoding="utf-8")
    text = ""
    for i in range (0,x):
        pageobj = pdfreader.pages[i]
        text += pageobj.extract_text()#.encode('latin-1')
    print(text)
    outputfile.write(text)
    outputfile.close()

if __name__ == '__main__':
    main()

# Denne trenger java installert så jeg dropper den
#from tika import parser # pip install tika
#filename = 'energi21'
#raw = parser.from_file(filename + '.pdf')
#sourcefile = open(filename + '.txt','w', encoding="utf-8")
#print(raw['content'],file = sourcefile)
#sourcefile.close()
