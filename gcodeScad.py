#!/usr/bin/env python3
#coding: utf-8

import sys
import numpy as np
from optparse import OptionParser

from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeInterpreter import GCodeInterpreter

class GCodeScad(GCodeInterpreter):
    def __init__(self, toolScad):
        GCodeInterpreter.__init__(self)
        self.toolScad = toolScad
        self.pathScad = ""
        
    def onMove(self, pos):
        p0 = self.currentPos
        p1 = pos
        self.pathScad += "cut([{:.4f},{:.4f},{:.4f}],[{:.4f},{:.4f},{:.4f}]) {};".format(
            p0[0],p0[1],p0[2],
            p1[0],p1[1],p1[2],
            self.toolScad)
        
def main(argv):
    optparser = OptionParser("usage: %prog [options] file.ngc ...")
    optparser.add_option("-v", action="store_true", dest="verbose", default=False, help="verbose output")
    optparser.add_option("--tool_type", metavar="value", action="store", type="int", dest="toolType", default=0, help="tool type (0 = square, 1 = ball, 2 = engraving)")
    optparser.add_option("--tool_diam", metavar="value", action="store", type="float", dest="toolDiam", default=0.25, help="tool diameter (inches)")
    optparser.add_option("--tool_doc", metavar="value", action="store", type="float", dest="toolDoc", default=0.75, help="tool depth of cut (inches)")
    optparser.add_option("--stock_size", metavar="X,Y,Z", action="store", type="string", dest="stockSize", default=None, help="stock size (inches)")
    optparser.add_option("--stock_pos", metavar="X,Y,Z", action="store", type="string", dest="stockPos", default=None, help="stock position (inches)")
    optparser.add_option("--fn", metavar="value", action="store", type="int", dest="fn", default=None, help="$fn override")
    (opts, args) = optparser.parse_args()
    
    if opts.toolType == 0:
        # square end mill
        toolScad = "translate([0,0,{:.4f}]) cylinder(h={:.4f},r1={:.4f}5,r2={:.4f},center=true)".format(opts.toolDoc/2,opts.toolDoc,opts.toolDiam/2,opts.toolDiam/2)
    elif opts.toolType == 1:
        # ball end mill
        toolScad = "union() {{ translate([0,0,{:.4f}]) cylinder(h={:.4f},r1={:.4f}5,r2={:.4f},center=true); translate([0,0,{:.4f}]) sphere(r={:.4f}); }}".format(opts.toolDoc/2,opts.toolDoc-opts.toolDiam/2,opts.toolDiam/2,opts.toolDiam/2,opts.toolDiam/2,opts.toolDiam/2)
    elif opts.toolType == 2:
        # engraving end mill
        toolScad = "translate([0,0,{:.4f}]) cylinder(h={:.4f},r1={:.4f}5,r2={:.4f},center=true)".format(opts.toolDoc/2,opts.toolDoc,0,opts.toolDiam/2)
    else:
        raise Exception("unknown tool type")

    engine = GCodeScad(toolScad)
    engine.verbose = opts.verbose

    for f in args:
        print(f, file=sys.stderr)
        input_stream = FileStream(f)
        lexer = GCodeLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = GCodeParser(stream)
        engine.visit(parser.ngcfile())

    if opts.stockSize:
        stockSize = np.fromstring(opts.stockSize, dtype=float, sep=',')
        stockPos = np.fromstring(opts.stockPos, dtype=float, sep=',') if opts.stockPos else np.array([0,0,-stockSize[2]])
    else:
        # default stock size based on machining bounds
        bounds = engine.maxPos-engine.minPos
        stockSize = [np.ceil(bounds[0]+0.1),np.ceil(bounds[1]+0.1),1.0]
        stockPos = [engine.minPos[0]-(stockSize[0]-bounds[0])/2,engine.minPos[1]-(stockSize[1]-bounds[1])/2,-stockSize[2]]
    pathScad = engine.pathScad
    if opts.fn:
        print("$fn={:n};".format(opts.fn))
    print("""module cut(p1,p2) {{
  hull() {{
    translate(p1) children();
    translate(p2) children();
  }}
}}
difference() {{
  translate([{:.4f},{:.4f},{:.4f}]) cube([{:.4f},{:.4f},{:.4f}]);
  {}
}};""".format(stockPos[0],stockPos[1],stockPos[2], stockSize[0],stockSize[1],stockSize[2], pathScad))

if __name__ == '__main__':
    main(sys.argv)
