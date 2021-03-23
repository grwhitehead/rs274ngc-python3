#!/usr/bin/env python3
#coding: utf-8

import sys
import numpy as np
from optparse import OptionParser

from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeInterpreter import GCodeInterpreter

def main(argv):
    optparser = OptionParser("usage: %prog [options] file.ngc ...")
    optparser.add_option("-v", action="store_true", dest="verbose", default=False, help="verbose output")
    (opts, args) = optparser.parse_args()

    engine = GCodeInterpreter()
    engine.verbose = opts.verbose
    
    for f in args:
        print(f, file=sys.stderr)
        input_stream = FileStream(f)
        lexer = GCodeLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = GCodeParser(stream)
        engine.visit(parser.ngcfile())

    if engine.dist > 0:
        print("min [{:.4f} {:.4f} {:.4f}]".format(*engine.minPos))
        print("max [{:.4f} {:.4f} {:.4f}]".format(*engine.maxPos))
        print("size [{:.4f} {:.4f} {:.4f}]".format(*(engine.maxPos-engine.minPos)))
    print("dist {:.4f} in".format(engine.dist))
    print("time {:.2f} sec".format(engine.time))

if __name__ == '__main__':
    main(sys.argv)
