#!/usr/bin/env python3
#coding: utf-8

import sys
import numpy as np
import matplotlib.pyplot as plt
from optparse import OptionParser

from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeInterpreter import GCodeInterpreter

class GCodePath(GCodeInterpreter):
    def __init__(self):
        GCodeInterpreter.__init__(self)
        self.path = []
    def onMove(self, pos):
        self.path.append(pos[0:3])

def main(argv):
    optparser = OptionParser("usage: %prog [options] file.ngc ...")
    optparser.add_option("-v", action="store_true", dest="verbose", default=False, help="verbose output")
    (opts, args) = optparser.parse_args()

    engine = GCodePath()
    engine.verbose = opts.verbose
    
    for f in args:
        print(f, file=sys.stderr)
        input_stream = FileStream(f)
        lexer = GCodeLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = GCodeParser(stream)
        engine.visit(parser.ngcfile())

    path = np.array(engine.path)
    np.set_printoptions(formatter={'float': '{:.4f}'.format})
    print(path)

    if engine.dist > 0:
        print("min [{:.4f} {:.4f} {:.4f}]".format(*engine.minPos))
        print("max [{:.4f} {:.4f} {:.4f}]".format(*engine.maxPos))
        print("size [{:.4f} {:.4f} {:.4f}]".format(*(engine.maxPos-engine.minPos)))
    print("dist {:.4f} in".format(engine.dist))
    print("time {:.2f} sec".format(engine.time))
        
    if len(path) > 0:
        fig = plt.figure()
        ba = path.max(axis=0)-path.min(axis=0)
        ba[ba==0] = 1
        ax = fig.add_subplot(111, projection='3d', box_aspect=ba)
        ax.plot(path[:,0],path[:,1],path[:,2])
        plt.show()

if __name__ == '__main__':
    main(sys.argv)
