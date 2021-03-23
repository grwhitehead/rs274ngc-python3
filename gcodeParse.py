#!/usr/bin/env python3
#coding: utf-8

import sys
import numpy as np
from optparse import OptionParser

from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser

def main(argv):
    optparser = OptionParser("usage: %prog [options] file.ngc ...")
    optparser.add_option("-v", action="store_true", dest="verbose", default=False, help="verbose output")
    (opts, args) = optparser.parse_args()

    for f in args:
        print(f, file=sys.stderr)
        input_stream = FileStream(f)
        lexer = GCodeLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = GCodeParser(stream)
        tree = parser.ngcfile()
        if opts.verbose:
            print(tree.toStringTree(recog=parser))
        
if __name__ == '__main__':
    main(sys.argv)
