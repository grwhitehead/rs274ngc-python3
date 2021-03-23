# Generated from GCode.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GCodeParser import GCodeParser
else:
    from GCodeParser import GCodeParser

# This class defines a complete generic visitor for a parse tree produced by GCodeParser.

class GCodeVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by GCodeParser#ngcfile.
    def visitNgcfile(self, ctx:GCodeParser.NgcfileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#program.
    def visitProgram(self, ctx:GCodeParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#line.
    def visitLine(self, ctx:GCodeParser.LineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#block_delete.
    def visitBlock_delete(self, ctx:GCodeParser.Block_deleteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#line_number.
    def visitLine_number(self, ctx:GCodeParser.Line_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#segment.
    def visitSegment(self, ctx:GCodeParser.SegmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#mid_line_word.
    def visitMid_line_word(self, ctx:GCodeParser.Mid_line_wordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#mid_line_letter.
    def visitMid_line_letter(self, ctx:GCodeParser.Mid_line_letterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#real_value.
    def visitReal_value(self, ctx:GCodeParser.Real_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#real_number.
    def visitReal_number(self, ctx:GCodeParser.Real_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#expression.
    def visitExpression(self, ctx:GCodeParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#binary_operation.
    def visitBinary_operation(self, ctx:GCodeParser.Binary_operationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#binary_operation1.
    def visitBinary_operation1(self, ctx:GCodeParser.Binary_operation1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#binary_operation2.
    def visitBinary_operation2(self, ctx:GCodeParser.Binary_operation2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#binary_operation3.
    def visitBinary_operation3(self, ctx:GCodeParser.Binary_operation3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#unary_combo.
    def visitUnary_combo(self, ctx:GCodeParser.Unary_comboContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#ordinary_unary_combo.
    def visitOrdinary_unary_combo(self, ctx:GCodeParser.Ordinary_unary_comboContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#ordinary_unary_operation.
    def visitOrdinary_unary_operation(self, ctx:GCodeParser.Ordinary_unary_operationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#arc_tangent_combo.
    def visitArc_tangent_combo(self, ctx:GCodeParser.Arc_tangent_comboContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#parameter_setting.
    def visitParameter_setting(self, ctx:GCodeParser.Parameter_settingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#parameter_value.
    def visitParameter_value(self, ctx:GCodeParser.Parameter_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#parameter_index.
    def visitParameter_index(self, ctx:GCodeParser.Parameter_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GCodeParser#comment.
    def visitComment(self, ctx:GCodeParser.CommentContext):
        return self.visitChildren(ctx)



del GCodeParser