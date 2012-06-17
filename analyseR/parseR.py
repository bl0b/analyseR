#!/usr/bin/env python
from jupyLR import Automaton
from scanneR import r_scanner
from grammar import R_grammar
from entities import *
from entities import RentityMeta


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

    def scoped_atom(self, ast):
        return Name(ast)

    def rightwards_assign(self, ast):
        return Assign(ast, True)

    def leftwards_assign(self, ast):
        return Assign(ast)

    def discard_semicolon(self, ast):
        return tuple()

    def validate_ast(self, ast):
        if ast[0] in RentityMeta.registry:
            ret = RentityMeta.registry[ast[0]](ast)
        elif hasattr(self, ast[0]):
            ret = getattr(self, ast[0])(ast)
        else:
            ret = ast
        #print ret
        if type(ret) is tuple and len(ret):
            print "untransformed", ret
        return ret

    def __call__(self, filename=None, text=None):
        if text is None and filename is not None:
            text = open(filename).read()
        elif text is not None:
            filename = '<text>'
        else:
            return None
        print "Parsing", filename
        RContext.current_file.append(filename)
        ret = Automaton.__call__(self, text)
        RContext.current_file.pop()
        return ret

#
R = ParseR()


def parse(filename=None, text=None):
    if RContext.current_file[-1] != '':
        print "[sourced by %s]" % RContext.current_file[-1],
    return R(filename, text)[0]

RContext.parse = staticmethod(parse)
