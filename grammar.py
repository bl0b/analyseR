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

R_grammar = """
-expression
    = e15
-e15= e13 | leftwards_assign
-e13= e12 | rightwards_assign
-e12= e11 | formula
-e11= e10 | bool_or
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
    | func_call
    | slot_extraction

slot_extraction
    = e1 DOLLAR name

indexing
    = e1 OPEN_SQ expression_list CLOSE_SQ
    | e1 OPEN_SQ OPEN_SQ expression_list CLOSE_SQ CLOSE_SQ

func_call
    = e1 OPEN_PAR expression_list CLOSE_PAR
    | e1 OPEN_PAR CLOSE_PAR

discard_semicolon
    = SEMICOLON

scoped_atom
    = scoped_atom SCOPE name
    | scoped_atom HIDDEN_SCOPE name
    | SYM

immed
    = STRING
    | CHAR
    | NUM

-atom
    = scoped_atom
    | immed
    | OPEN_PAR expression CLOSE_PAR
    | func_decl

func_decl
    = FUNCTION OPEN_PAR param_list CLOSE_PAR bloc
    | FUNCTION OPEN_PAR CLOSE_PAR bloc

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
    = e2 CIRCONFLEX NUM

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

script
    = statements

-statements
    = statements statement
    | statement

statement
    = raw_statement
    | raw_statement discard_semicolon
    | discard_semicolon
    | raw_statement

-raw_statement
    = expression
    | SOURCE OPEN_PAR STRING CLOSE_PAR
    | IF OPEN_PAR expression CLOSE_PAR statement
    | IF OPEN_PAR expression CLOSE_PAR statement ELSE statement
    | FOR OPEN_PAR SYM IN expression CLOSE_PAR statement
    | WHILE OPEN_PAR expression CLOSE_PAR statement
    | REPEAT statement
    | RETURN OPEN_PAR expression CLOSE_PAR
    | bloc

-expression_list
    = expression_list COMMA expression
    | expression
    | COMMA expression_list
    | expression_list COMMA

-name
    = SYM
    | STRING
"""
