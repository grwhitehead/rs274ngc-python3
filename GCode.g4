//
// NIST RS274NGC Version 3
//
// https://www.nist.gov/publications/nist-rs274ngc-interpreter-version-3
//

grammar GCode;


ngcfile
    : '%' EOL program '%' EOL .*? EOF
    | '%' EOL program EOF // not strict
    | program EOF
    ;

program
    : line*
    ;

line
    : block_delete? line_number? segment* EOL
    ;

block_delete
    : '/'
    ;

line_number
    : N DIGIT DIGIT? DIGIT? DIGIT? DIGIT?
    ;

segment
    : mid_line_word
    | parameter_setting
    | comment
    ;

mid_line_word
    : mid_line_letter real_value
    ;

mid_line_letter
    : A
    | B
    | C
    | D
    | E // not strict
    | F
    | G
    | H
    | I
    | J
    | K
    | L
    | M
    | O // not strict
    | P
    | Q
    | R
    | S
    | T
    | U // not strict
    | V // not strict
    | W // not strict
    | X
    | Y
    | Z
    ;

real_value
    : real_number
    | expression
    | parameter_value
    | unary_combo
    ;

real_number
    : (PLUS | MINUS)? DIGIT+ (DECIMAL_POINT DIGIT*)?
    | (PLUS | MINUS)? DECIMAL_POINT DIGIT+
    ;

expression
    : LEFT_BRACKET real_value (binary_operation real_value)* RIGHT_BRACKET
    ;

binary_operation
    : binary_operation1
    | binary_operation2
    | binary_operation3
    ;

binary_operation1
    : POWER
    ;

binary_operation2
    : DIVIDED_BY
    | MODULO
    | TIMES
    ;

binary_operation3
    : LOGICAL_AND
    | EXCLUSIVE_OR
    | MINUS
    | NON_EXCLUSIVE_OR
    | PLUS
    ;

unary_combo
    : ordinary_unary_combo
    | arc_tangent_combo
    ;

ordinary_unary_combo
    : ordinary_unary_operation expression
    ;

ordinary_unary_operation
    : ABSOLUTE_VALUE
    | ARC_COSINE
    | ARC_SINE
    | COSINE
    | E_RAISED_TO
    | FIX_DOWN
    | FIX_UP
    | NATURAL_LOG_OF
    | ROUND_OPERATION
    | SINE
    | SQUARE_ROOT
    | TANGENT
    ;

arc_tangent_combo
    : ARC_TANGENT expression DIVIDED_BY expression
    ;

parameter_setting
    : PARAMETER_SIGN parameter_index EQUAL_SIGN real_value
    ;

parameter_value
    : PARAMETER_SIGN parameter_index
    ;

parameter_index
    : real_value
    ;

comment
    : COMMENT
    ;


A
    : [Aa]
    ;

B
    : [Bb]
    ;

C
    : [Cc]
    ;
D
    : [Dd]
    ;

E
    : [Ee]
    ;

F
    : [Ff]
    ;

G
    : [Gg]
    ;

H
    : [Hh]
    ;

I
    : [Ii]
    ;

J
    : [Jj]
    ;

K
    : [Kk]
    ;

L
    : [Ll]
    ;

M
    : [Mm]
    ;

N
    : [Nn]
    ;

O
    : [Oo]
    ;

P
    : [Pp]
    ;

Q
    : [Qq]
    ;

R
    : [Rr]
    ;

S
    : [Ss]
    ;

T
    : [Tt]
    ;

U
    : [Uu]
    ;

V
    : [Vv]
    ;

W
    : [Ww]
    ;

X
    : [Xx]
    ;

Y
    : [Yy]
    ;

Z
    : [Zz]
    ;

PLUS
    : '+'
    ;
MINUS
    : '-'
    ;

DECIMAL_POINT
    : '.'
    ;

DIGIT
    : '0'
    | '1'
    | '2'
    | '3'
    | '4'
    | '5'
    | '6'
    | '7'
    | '8'
    | '9'
    ;

LEFT_BRACKET
    : '['
    ;

RIGHT_BRACKET
    : ']'
    ;

POWER
    : '**'
    ;

DIVIDED_BY
    : '/'
    ;

MODULO
    : 'mod'
    | 'MOD'
    ;

TIMES
    : '*'
    ;

LOGICAL_AND
    : [Aa][Nn][Dd]
    ;

EXCLUSIVE_OR
    : [Xx][Oo][Rr]
    ;

NON_EXCLUSIVE_OR
    : [Oo][Rr]
    ;

ABSOLUTE_VALUE
    : [Aa][Bb][Ss]
    ;

ARC_COSINE
    : [Aa][Cc][Oo][Ss]
    ;

ARC_SINE
    : [Aa][Ss][Ii][Nn]
    ;

COSINE
    : [Cc][Oo][Ss]
    ;

E_RAISED_TO
    : [Ee][Xx][Pp]
    ;

FIX_DOWN
    : [Ff][Ii][Xx]
    ;

FIX_UP
    : [Ff][Uu][Pp]
    ;

NATURAL_LOG_OF
    : [Ll][Nn]
    ;

ROUND_OPERATION
    : [Rr][Oo][Uu][Nn][Dd]
    ;

SINE
    : [Ss][Ii][Nn]
    ;

SQUARE_ROOT
    : [Ss][Qq][Rr][Tt]
    ;

TANGENT
    : [Tt][Aa][Nn]
    ;

ARC_TANGENT
    : [Aa][Tt][Aa][Nn]
    ;

PARAMETER_SIGN
    : '#'
    ;

EQUAL_SIGN
    : '='
    ;


COMMENT
    : '('~(')')*')'
    | ';'~([\r\n])* // not strict
    ;

EOL
    : '\r'
    | '\n'
    | '\r\n'
    ;

WS
    : [ \t] + -> skip
    ;
