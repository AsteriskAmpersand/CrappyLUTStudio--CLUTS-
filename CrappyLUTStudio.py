# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:41:25 2023

@author: Asterisk
"""
from LUT import LUT_Tex
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='Handles LUTs for MHW')
parser.add_argument('input_filenames',nargs = '+', help='list of input files with extension, use idem as an input filename to generate the identity LUT table')
parser.add_argument('-s', '--stack', dest = 'stack', action='store_true',help = 'stack multiple filters and apply them sequentially before storing the result')
parser.add_argument('-o', '-output', dest = 'output', default = "", type = str, help='output file name (with extension), if converting multiple non-stacking files use first input filename as replacement string')

if __name__ in "__main__":
    args = parser.parse_args()
    if not args.stack:
        outbase = Path(args.output) if args.output else None
        inbase = Path(args.input_filenames[0]).stem
        for f in args.input_filenames:
            noutput = str(outbase).replace(inbase,Path(f).stem) if outbase else None
            print("Converting %s -> %s"%(f,noutput))
            LUT_Tex.convert(f,noutput)
    else:
        if not args.output:
            print("Stack conversion requires explicit output name")
        else:
            print("Stacking %s ==> %s"%(" -> ".join(map(lambda x: Path(x).stem, args.input_filenames)),args.output))
            LUT_Tex.stack(args.output,*args.input_filenames)