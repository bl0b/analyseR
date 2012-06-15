#!/usr/bin/env python
from jupyLR import Automaton
from scanner import r_scanner


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
-e1 = e0  | indexing | func_call
-e0 = slot_extraction
    | atom

-opt_nl =| discard_nl

discard_semicolon
    = SEMICOLON

discard_nl
    = NEWLINE

scoped_atom
    = scoped_atom SCOPE name
    | scoped_atom HIDDEN_SCOPE name
    | SYM

immed
    = STRING
    | CHAR
    | INT_HEX
    | INT_DEC
    | INT_OCT
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
    = param_list opt_nl COMMA param
    | param

param
    = opt_nl name opt_nl EQUAL opt_nl expression opt_nl
    | opt_nl name opt_nl

func_call
    = e1 OPEN_PAR expression_list CLOSE_PAR
    | e1 OPEN_PAR CLOSE_PAR

slot_extraction
    = e0 DOLLAR name

indexing
    = e1 OPEN_SQ expression_list CLOSE_SQ
    | e1 OPEN_SQ OPEN_SQ expression_list CLOSE_SQ CLOSE_SQ

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
    = raw_statement discard_nl
    | raw_statement discard_semicolon
    | discard_semicolon
    | discard_nl
    | raw_statement

-raw_statement
    = expression
    | SOURCE OPEN_PAR STRING CLOSE_PAR
    | IF OPEN_PAR expression CLOSE_PAR statement
    | IF OPEN_PAR expression CLOSE_PAR statement ELSE statement
    | FOR OPEN_PAR SYM IN expression CLOSE_PAR statement
    | bloc

-expression_list
    = opt_nl expression_list opt_nl COMMA opt_nl expression opt_nl
    | opt_nl expression opt_nl
    | opt_nl COMMA opt_nl expression_list opt_nl
    | opt_nl expression_list opt_nl COMMA opt_nl

-name
    = SYM
    | STRING
"""


class Rentity(object):

    def __repr__(self):
        return str(self)


class Source(Rentity):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'Source(' + self.filename + ')'

    def eval(self):
        return None


class Function(Rentity):

    def __init__(self, ast):
        self.ast = ast
        self.name = None

    def __str__(self):
        return ('Function'
                + (self.name and ':' + str(self.name) or '')
                + str(self.ast[1:]))

    def make_name(self, name):
        ret = Function(self.ast)
        ret.name = name
        return ret

    def eval(self):
        return self


class Assign(Rentity):

    def __new__(self, ast, rightwards=False):
        if rightwards:
            n, f = 3, 1
        else:
            n, f = 1, 3
        if type(ast[n]) is Name and type(ast[f]) is Function:
            return ast[f].make_name(ast[n])
        return Rentity.__new__(Assign)

    def __init__(self, ast, rightwards=False):
        if rightwards:
            self.lhs = ast[3]
            self.rhs = ast[1]
        else:
            self.lhs = ast[1]
            self.rhs = ast[3]

    def __str__(self):
        return 'Assign(lhs=' + str(self.lhs) + ', rhs=' + str(self.rhs) + ')'

    def eval(self):
        return self.rhs


class Bloc(Rentity, tuple):

    def __new__(cls, ast):
        return tuple.__new__(cls, ast[2:-1])

    def __str__(self):
        return 'Bloc(' + str(len(self)) + ' statements)'


class If(Rentity):

    def __init__(self, ast):
        self.cond = ast[3]
        self.then = ast[5]
        self.els_ = len(ast) == 7 and ast[7] or None

    def __str__(self):
        ret = 'If(cond=' + str(self.cond) + ', then=' + str(self.then)
        if self.els_ is not None:
            ret += ', else=' + str(self.els_)
        ret += ')'
        return ret


class Immed(Rentity):

    def __init__(self, ast):
        self.typ = ast[1][0]
        self.val = ast[1][1]

    def __str__(self):
        return str(self.typ) + '(' + str(self.val) + ')'


class Name(Rentity):

    def __init__(self, ast):
        if len(ast) == 4:
            self.namespace = type(ast[1]) is tuple and ast[1][1] or ast[1]
            self.visibility = ast[2][1]
            self.name = ast[3][1]
        else:
            self.namespace = None
            self.visibility = None
            self.name = ast[1][1]

    def __str__(self):
        ret = 'Name('
        if self.namespace is not None:
            ret += str(self.namespace)
            ret += self.visibility
        ret += self.name
        ret += ')'
        return ret


class Param(Rentity):

    def __init__(self, ast):
        if type(ast) is Assign:
            # named parameter
            self.name = ast.lhs
            self.value = ast.rhs
        else:
            self.name = None
            self.value = ast

    def __str__(self):
        ret = 'Param('
        if self.name:
            ret += 'name=' + str(self.name.name) + ', '
        ret += 'value=' + str(self.value) + ')'
        return ret


class Call(Rentity):

    def __init__(self, ast):
        self.callee = ast[1]
        self.params = tuple(Param(x) for x in ast[3::2])

    def __str__(self):
        return ('Call(callee=' + str(self.callee) + ', params='
                + str(self.params) + ')')


class ParseR(Automaton):

    def __init__(self):
        Automaton.__init__(self, "script", R_grammar, r_scanner)
        self.resolve_SR_conflicts(favor='S')

    def statement(self, ast):
        if len(ast) == 1:
            return tuple()
        elif isinstance(ast[1], Rentity):
            return ast[1]
        elif type(ast[1]) is tuple:
            if ast[1][0] == 'SOURCE':
                return Source(ast[3][1])
            elif ast[1][0] == 'IF':
                return If(ast)
        return ast

    def immed(self, ast):
        return Immed(ast)

    def func_call(self, ast):
        return Call(ast)

    def scoped_atom(self, ast):
        return Name(ast)

    def bloc(self, ast):
        return Bloc(ast)

    def script(self, ast):
        return ast[1:]

    def discard_nl(self, ast):
        return tuple()

    def discard_semicolon(self, ast):
        return tuple()

    def func_decl(self, ast):
        return Function(ast)

    def rightwards_assign(self, ast):
        return Assign(ast, True)

    def leftwards_assign(self, ast):
        return Assign(ast)

    def validate_ast(self, ast):
        if(hasattr(self, ast[0])):
            ret = getattr(self, ast[0])(ast)
        else:
            ret = ast
        #print ret
        return ret

#
p = ParseR()
