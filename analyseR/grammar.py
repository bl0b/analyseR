#!/usr/bin/env python

# http://stat.ethz.ch/R-manual/R-patched/library/base/html/Syntax.html
# The following unary and binary operators are defined. They are listed in
# precedence groups, from highest to lowest. :: :::	 access variables in a
# namespace.
# $ @	 component / slot extraction                    0
# [ [[	 indexing                                       1
# ^	 exponentiation (right to left)                     2
# - +	 unary minus and plus                           3
# :	 sequence operator                                  4
# %any%	 special operators (including %% and %/%)       5
# * /	 multiply, divide                               6
# + -	 (binary) add, subtract                         7
# < > <= >= == !=	 ordering and comparison            8
# !	 negation                                           9
# & &&	 and                                            10
# | ||	 or                                             11
# ~	 as in formulae                                     12
# -> ->>	 rightwards assignment                      13
# =	 assignment (right to left)                         14
# <- <<-	 assignment (right to left)                 15
# ?	 help (unary and binary)                            16

# help operator is left unimplemented.
# start symbol is 'script'.


# turns out any statement is also an expression.
# if (1) { 4 } else { 5 } + 10   => 4
# if (0) { 4 } else { 5 } + 10   => 15


# Operator precedence

R_grammar = ("""
-expression
    = e15
-e15= e13 | leftwards_assign
-e13= e12 | rightwards_assign
-e12= e11 | formula
-e11= e10 | bool_or | statement
-e10= e9  | bool_and
-e9 = e8  | negation
-e8 = e7  | comparison
-e7 = e6  | addsub
-e6 = e5  | muldiv
-e5 = e4  | special_op
-e4 = e3  | sequence
-e3 = e2  | unary_plus_or_minus
-e2 = e1  | exponentiation
-e1 = atom
    | indexing
    | call
    | slot_extraction
"""

# Operations

+ """
slot_extraction
    = e1 DOLLAR name

indexing
    = e1 OPEN_SQ expression_list CLOSE_SQ
    | e1 OPEN_SQ OPEN_SQ expression_list CLOSE_SQ CLOSE_SQ

call
    = e1 OPEN_PAR expression_list CLOSE_PAR
    | e1 OPEN_PAR CLOSE_PAR

scoped_atom
    = scoped_atom SCOPE name
    | scoped_atom HIDDEN_SCOPE name
    | SYM

immed
    = STRING
    | NUM

-atom
    = scoped_atom
    | immed
    | subexpr
    | function
    | bloc

function
    = FUNCTION OPEN_PAR param_list CLOSE_PAR expression
    | FUNCTION OPEN_PAR CLOSE_PAR expression

bloc
    = OPEN_CURLY statements CLOSE_CURLY
    | OPEN_CURLY CLOSE_CURLY

param_list
    = param_list COMMA param
    | param

param
    = name EQUAL expression
    | name

exponentiation
    = e2 CIRCONFLEX immed

unary_plus_or_minus
    = PLUS e2
    | MINUS e2

sequence
    = e3 COLON e3

special_op
    = e5 SPECIAL_OP e4

muldiv
    = e6 STAR e5
    | e6 SLASH e5

addsub
    = e7 PLUS e6
    | e7 MINUS e6

comparison
    = e7 EQ e7
    | e7 NE e7
    | e7 INF e7
    | e7 SUP e7
    | e7 LE e7
    | e7 GE e7

negation
    = EXCLAMATION e8

bool_and
    = e10 AMPERSAND e9
    | e10 LOG_AND e9

bool_or
    = e11 PIPE e9
    | e11 LOG_OR e9

formula
    = e11 TILDE e11

rightwards_assign
    = e12 RIGHT_ARROW e11
    | e12 RIGHT_ARROW2 e11

leftwards_assign
    = e12 LEFT_ARROW e13
    | e12 LEFT_ARROW2 e13
    | e12 EQUAL e13

"""

# Statements

+ """
-statements
    = statements toplevel_statement
    | statements expression
    | toplevel_statement

-toplevel_statement
    = expression statement_separator
    | statement_separator

-statement
    = source
    | if
    | for
    | return
    | while
    | repeat

source
    = SOURCE OPEN_PAR STRING CLOSE_PAR
    | SOURCE OPEN_PAR STRING COMMA param_list CLOSE_PAR

repeat
    = REPEAT expression

while
    = WHILE OPEN_PAR expression CLOSE_PAR expression

if  = IF OPEN_PAR expression CLOSE_PAR expression
    | IF OPEN_PAR expression CLOSE_PAR expression ELSE expression

for = FOR OPEN_PAR SYM IN expression CLOSE_PAR expression

return
    = RETURN OPEN_PAR expression CLOSE_PAR
"""

# Structure / Misc

+ """
script
    = statements

statement_separator
    = SEMICOLON
    | NEWLINE

subexpr
    = OPEN_PAR expression CLOSE_PAR

expression_list
    = _elist

-_elist
    = _elist COMMA expression
    | expression
    | COMMA _elist
    | _elist COMMA

-name
    = SYM
    | STRING
""")
