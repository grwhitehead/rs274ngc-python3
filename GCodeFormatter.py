import sys
import math

from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeVisitor import GCodeVisitor


class GCodeFormatter(GCodeVisitor):

    def __init__(self):
        GCodeVisitor.__init__(self)

    def defaultResult(self):
        return ""
    
    def aggregateResult(self, aggregate, nextResult):
        if len(nextResult) > 0 and len(aggregate) > 0 and not aggregate.endswith("\n"):
            aggregate +=" "
        return aggregate+nextResult
    

    def visitNgcfile(self, ctx:GCodeParser.NgcfileContext):
        return self.visitChildren(ctx)

    def visitProgram(self, ctx:GCodeParser.ProgramContext):
        return self.visitChildren(ctx)

    def visitLine(self, ctx:GCodeParser.LineContext):
        return self.visitChildren(ctx)+"\n"

    def visitLine_number(self, ctx:GCodeParser.Line_numberContext):
        return ctx.getText()

    def visitSegment(self, ctx:GCodeParser.SegmentContext):
        return self.visitChildren(ctx)

    def visitMid_line_word(self, ctx:GCodeParser.Mid_line_wordContext):
        return self.visitChildren(ctx)

    def visitMid_line_letter(self, ctx:GCodeParser.Mid_line_letterContext):
        return ctx.getText()

    def visitReal_value(self, ctx:GCodeParser.Real_valueContext):
        return self.visitChildren(ctx)

    def visitReal_number(self, ctx:GCodeParser.Real_numberContext):
        return ctx.getText()

    def visitExpression(self, ctx:GCodeParser.ExpressionContext):
        return "["+self.visitChildren(ctx)+"]"

    def visitBinary_operation(self, ctx:GCodeParser.Binary_operationContext):
        return ctx.getText().lower()

    def visitUnary_combo(self, ctx:GCodeParser.Unary_comboContext):
        return self.visitChildren(ctx)

    def visitOrdinary_unary_combo(self, ctx:GCodeParser.Ordinary_unary_comboContext):
        return ctx.ordinary_unary_operation().getText().lower()+self.visit(ctx.expression())

    def visitArc_tangent_combo(self, ctx:GCodeParser.Arc_tangent_comboContext):
        return "atan"+self.visit(ctx.expression(0))+"/"+self.visit(ctx.expression(1))

    def visitParameter_setting(self, ctx:GCodeParser.Parameter_settingContext):
        #return self.visitChildren(ctx)
        return "#"+self.visit(ctx.parameter_index())+"="+self.visit(ctx.real_value())

    def visitParameter_value(self, ctx:GCodeParser.Parameter_valueContext):
        return "#"+self.visitChildren(ctx)

    def visitParameter_index(self, ctx:GCodeParser.Parameter_indexContext):
        return self.visitChildren(ctx)

    def visitComment(self, ctx:GCodeParser.CommentContext):
        return ctx.getText()
