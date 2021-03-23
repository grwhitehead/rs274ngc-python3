import sys
import math

from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeVisitor import GCodeVisitor
from GCodeParamMemory import GCodeParamMemory


class GCodeExprEvaluator(GCodeVisitor):

    def __init__(self, paramMemory):
        GCodeVisitor.__init__(self)
        self.paramMemory = paramMemory

    def visitReal_number(self, ctx:GCodeParser.Real_valueContext):
        return float(ctx.getText())
    
    def visitExpression(self, ctx:GCodeParser.ExpressionContext):
        #
        # LEFT_BRACKET real_value (binary_operation real_value)* RIGHT_BRACKET
        #
        # evaluate infix expression using Dijkstra's stack-based algorithm
        #
        operands = ctx.real_value();
        operandStack = [self.visit(operands[0])]
        operands_i = 1
        operators = ctx.binary_operation()
        operatorStack = []
        operators_i = 0
        while operators_i < len(operators):
            nextOperator = operators[operators_i]
            operators_i += 1
            nextOperand = self.visit(operands[operands_i])
            operands_i += 1
            while len(operatorStack) > 0 and _binaryOperatorPrecedence(nextOperator) > _binaryOperatorPrecedence(operatorStack[-1]):
                o = operatorStack.pop()
                r = operandStack.pop()
                l = operandStack.pop()
                operandStack.append(_binaryOperationResult(l,o,r))
            operandStack.append(nextOperand)
            operatorStack.append(nextOperator)
        while len(operatorStack) > 0:
            op = operatorStack.pop()
            r = operandStack.pop()
            l = operandStack.pop()
            operandStack.append(_binaryOperationResult(l,op,r))
        return operandStack[0]

    def visitParameter_value(self, ctx:GCodeParser.Parameter_valueContext):
        return self.paramMemory.getValue(int(self.visit(ctx.parameter_index().real_value())))

    def visitUnary_combo(self, ctx:GCodeParser.Unary_comboContext):
        if ctx.ordinary_unary_combo():
            return _unaryOperationResult(ctx.ordinary_unary_combo().ordinary_unary_operation(),self.visit(ctx.ordinary_unary_combo().expression()))
        elif ctx.arc_tangent_combo():
            return _arcTangentResult(self.visit(ctx.arc_tangent_combo().expression(0)), self.visit(ctx.arc_tangent_combo().expression(1)))


def _binaryOperatorPrecedence(op):
    if op.binary_operation1():
        return 1
    if op.binary_operation2():
        return 2
    if op.binary_operation3():
        return 3
    return 0

def _binaryOperationResult(l, op, r):
    if op.binary_operation1():
        if op.binary_operation1().POWER():
            return math.pow(l,r)
    if op.binary_operation2():
        if op.binary_operation2().DIVIDED_BY():
            return l / r;
        elif op.binary_operation2().MODULO():
            return l % r;
        elif op.binary_operation2().TIMES():
            return l * r;
    if op.binary_operation3():
        if op.binary_operation3().LOGICAL_AND():
            return 1 if l and r else 0;
        elif op.binary_operation3().EXCLUSIVE_OR():
            return 1 if (l or r) and not(l and r) else 0;
        elif op.binary_operation3().MINUS():
            return l - r;
        elif op.binary_operation3().NON_EXCLUSIVE_OR():
            return 1 if l or r else 0;
        elif op.binary_operation3().PLUS():
            return l + r;
    raise GCodeException("unknown operation")

def _unaryOperationResult(op, v):
    if op.ABSOLUTE_VALUE():
        return math.fabs(v)
    elif op.ARC_COSINE():
        return math.degrees(math.acos(v))
    elif op.ARC_SINE():
        return math.degrees(math.asin(v))
    elif op.COSINE():
        return math.cos(math.radians(v))
    elif op.E_RAISED_TO():
        return math.exp(v)
    elif op.FIX_DOWN():
        return math.floor(v)
    elif op.FIX_UP():
        return math.ceil(v)
    elif op.NATURAL_LOG_OF():
        return math.log(v)
    elif op.ROUND_OPERATION():
        return math.floor(v+0.5)
    elif op.SINE():
        return math.sin(math.radians(v))
    elif op.SQUARE_ROOT():
        return math.sqrt(v)
    elif op.TANGENT():
        return math.tan(math.radians(v))
    raise GCodeException("unknown unary operator")

def _arcTangentResult(y, x):
    return math.degrees(math.atan2(y, x))
