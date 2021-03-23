# Generated from GCode.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GCodeParser import GCodeParser
else:
    from GCodeParser import GCodeParser

# This class defines a complete listener for a parse tree produced by GCodeParser.
class GCodeListener(ParseTreeListener):

    # Enter a parse tree produced by GCodeParser#ngcfile.
    def enterNgcfile(self, ctx:GCodeParser.NgcfileContext):
        pass

    # Exit a parse tree produced by GCodeParser#ngcfile.
    def exitNgcfile(self, ctx:GCodeParser.NgcfileContext):
        pass


    # Enter a parse tree produced by GCodeParser#program.
    def enterProgram(self, ctx:GCodeParser.ProgramContext):
        pass

    # Exit a parse tree produced by GCodeParser#program.
    def exitProgram(self, ctx:GCodeParser.ProgramContext):
        pass


    # Enter a parse tree produced by GCodeParser#line.
    def enterLine(self, ctx:GCodeParser.LineContext):
        pass

    # Exit a parse tree produced by GCodeParser#line.
    def exitLine(self, ctx:GCodeParser.LineContext):
        pass


    # Enter a parse tree produced by GCodeParser#block_delete.
    def enterBlock_delete(self, ctx:GCodeParser.Block_deleteContext):
        pass

    # Exit a parse tree produced by GCodeParser#block_delete.
    def exitBlock_delete(self, ctx:GCodeParser.Block_deleteContext):
        pass


    # Enter a parse tree produced by GCodeParser#line_number.
    def enterLine_number(self, ctx:GCodeParser.Line_numberContext):
        pass

    # Exit a parse tree produced by GCodeParser#line_number.
    def exitLine_number(self, ctx:GCodeParser.Line_numberContext):
        pass


    # Enter a parse tree produced by GCodeParser#segment.
    def enterSegment(self, ctx:GCodeParser.SegmentContext):
        pass

    # Exit a parse tree produced by GCodeParser#segment.
    def exitSegment(self, ctx:GCodeParser.SegmentContext):
        pass


    # Enter a parse tree produced by GCodeParser#mid_line_word.
    def enterMid_line_word(self, ctx:GCodeParser.Mid_line_wordContext):
        pass

    # Exit a parse tree produced by GCodeParser#mid_line_word.
    def exitMid_line_word(self, ctx:GCodeParser.Mid_line_wordContext):
        pass


    # Enter a parse tree produced by GCodeParser#mid_line_letter.
    def enterMid_line_letter(self, ctx:GCodeParser.Mid_line_letterContext):
        pass

    # Exit a parse tree produced by GCodeParser#mid_line_letter.
    def exitMid_line_letter(self, ctx:GCodeParser.Mid_line_letterContext):
        pass


    # Enter a parse tree produced by GCodeParser#real_value.
    def enterReal_value(self, ctx:GCodeParser.Real_valueContext):
        pass

    # Exit a parse tree produced by GCodeParser#real_value.
    def exitReal_value(self, ctx:GCodeParser.Real_valueContext):
        pass


    # Enter a parse tree produced by GCodeParser#real_number.
    def enterReal_number(self, ctx:GCodeParser.Real_numberContext):
        pass

    # Exit a parse tree produced by GCodeParser#real_number.
    def exitReal_number(self, ctx:GCodeParser.Real_numberContext):
        pass


    # Enter a parse tree produced by GCodeParser#expression.
    def enterExpression(self, ctx:GCodeParser.ExpressionContext):
        pass

    # Exit a parse tree produced by GCodeParser#expression.
    def exitExpression(self, ctx:GCodeParser.ExpressionContext):
        pass


    # Enter a parse tree produced by GCodeParser#binary_operation.
    def enterBinary_operation(self, ctx:GCodeParser.Binary_operationContext):
        pass

    # Exit a parse tree produced by GCodeParser#binary_operation.
    def exitBinary_operation(self, ctx:GCodeParser.Binary_operationContext):
        pass


    # Enter a parse tree produced by GCodeParser#binary_operation1.
    def enterBinary_operation1(self, ctx:GCodeParser.Binary_operation1Context):
        pass

    # Exit a parse tree produced by GCodeParser#binary_operation1.
    def exitBinary_operation1(self, ctx:GCodeParser.Binary_operation1Context):
        pass


    # Enter a parse tree produced by GCodeParser#binary_operation2.
    def enterBinary_operation2(self, ctx:GCodeParser.Binary_operation2Context):
        pass

    # Exit a parse tree produced by GCodeParser#binary_operation2.
    def exitBinary_operation2(self, ctx:GCodeParser.Binary_operation2Context):
        pass


    # Enter a parse tree produced by GCodeParser#binary_operation3.
    def enterBinary_operation3(self, ctx:GCodeParser.Binary_operation3Context):
        pass

    # Exit a parse tree produced by GCodeParser#binary_operation3.
    def exitBinary_operation3(self, ctx:GCodeParser.Binary_operation3Context):
        pass


    # Enter a parse tree produced by GCodeParser#unary_combo.
    def enterUnary_combo(self, ctx:GCodeParser.Unary_comboContext):
        pass

    # Exit a parse tree produced by GCodeParser#unary_combo.
    def exitUnary_combo(self, ctx:GCodeParser.Unary_comboContext):
        pass


    # Enter a parse tree produced by GCodeParser#ordinary_unary_combo.
    def enterOrdinary_unary_combo(self, ctx:GCodeParser.Ordinary_unary_comboContext):
        pass

    # Exit a parse tree produced by GCodeParser#ordinary_unary_combo.
    def exitOrdinary_unary_combo(self, ctx:GCodeParser.Ordinary_unary_comboContext):
        pass


    # Enter a parse tree produced by GCodeParser#ordinary_unary_operation.
    def enterOrdinary_unary_operation(self, ctx:GCodeParser.Ordinary_unary_operationContext):
        pass

    # Exit a parse tree produced by GCodeParser#ordinary_unary_operation.
    def exitOrdinary_unary_operation(self, ctx:GCodeParser.Ordinary_unary_operationContext):
        pass


    # Enter a parse tree produced by GCodeParser#arc_tangent_combo.
    def enterArc_tangent_combo(self, ctx:GCodeParser.Arc_tangent_comboContext):
        pass

    # Exit a parse tree produced by GCodeParser#arc_tangent_combo.
    def exitArc_tangent_combo(self, ctx:GCodeParser.Arc_tangent_comboContext):
        pass


    # Enter a parse tree produced by GCodeParser#parameter_setting.
    def enterParameter_setting(self, ctx:GCodeParser.Parameter_settingContext):
        pass

    # Exit a parse tree produced by GCodeParser#parameter_setting.
    def exitParameter_setting(self, ctx:GCodeParser.Parameter_settingContext):
        pass


    # Enter a parse tree produced by GCodeParser#parameter_value.
    def enterParameter_value(self, ctx:GCodeParser.Parameter_valueContext):
        pass

    # Exit a parse tree produced by GCodeParser#parameter_value.
    def exitParameter_value(self, ctx:GCodeParser.Parameter_valueContext):
        pass


    # Enter a parse tree produced by GCodeParser#parameter_index.
    def enterParameter_index(self, ctx:GCodeParser.Parameter_indexContext):
        pass

    # Exit a parse tree produced by GCodeParser#parameter_index.
    def exitParameter_index(self, ctx:GCodeParser.Parameter_indexContext):
        pass


    # Enter a parse tree produced by GCodeParser#comment.
    def enterComment(self, ctx:GCodeParser.CommentContext):
        pass

    # Exit a parse tree produced by GCodeParser#comment.
    def exitComment(self, ctx:GCodeParser.CommentContext):
        pass



del GCodeParser