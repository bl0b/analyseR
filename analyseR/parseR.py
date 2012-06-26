#!/usr/bin/env python
from jupyLR import Automaton
from scanneR import r_scanner
from grammar import R_grammar
from entities import *
from entities import RentityMeta
import os
import cPickle


ANALYZERCACHEDIR = os.path.join(os.getenv('HOME'), '.analyzeRcache')
ANALYZERCACHE_GRAMMAR = os.path.join(ANALYZERCACHEDIR, 'R_grammar')
ANALYZERCACHE_PARSER = os.path.join(ANALYZERCACHEDIR, 'parser.pkl')

if not os.path.isdir(ANALYZERCACHEDIR):
    os.makedirs(ANALYZERCACHEDIR)

if os.path.exists(ANALYZERCACHE_GRAMMAR):
    analyzeRcached_grammar = open(ANALYZERCACHE_GRAMMAR).read()
else:
    analyzeRcached_grammar = ''


class ParseR(Automaton):

    def __init__(self):
        from time import time
        t0 = time()
        Automaton.__init__(self, "script", R_grammar, r_scanner)
        self.resolve_SR_conflicts(favor='S')
        self.build_time = time() - t0
        #self.debug = True

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

    def toplevel_statement(self, ast):
        #print "toplevel_statement", ast
        if len(ast) > 1 and isinstance(ast[1], Rentity):
            return ast[1]
        return tuple()

    def statement_separator(self, ast):
        return tuple()

    def discard_nls(self, ast):
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
            RContext.current_text.append(open(filename).read())
            #RContext.current_dir.append(os.path.dirname(filename))
        elif text is not None:
            filename = '<text>'
            RContext.current_text.append(text)
            #RContext.current_dir.append(RContext.current_dir[-1])
        else:
            return None
        print "Parsing", filename
        RContext.current_file.append(filename)
        try:
            ret = Automaton.__call__(self, RContext.current_text[-1])
        except:
            import traceback
            traceback.print_exc()
            ret = None
        RContext.current_file.pop()
        RContext.current_text.pop()
        #RContext.current_dir.pop()
        return ret

#


def init_parser():
    R = ParseR()

    #print "LR conflicts", R.conflicts()

    conflicts = R.conflicts()

    if conflicts:
        print "LR conflicts summary:"

        def is_RR(c):
            s, t = c
            return reduce(lambda a, (ac, dest): a and ac == 'R',
                          R.ACTION[s][t],
                          True)

        rr = len(filter(is_RR, conflicts))
        print rr, "R/R conflicts"
        print len(conflicts) - rr, "S/R conflicts"
        states = set(c[0] for c in conflicts)
        for st in states:
            print R.itemsetstr(R.closure(R.LR0[st]), label=str(st))
            for s, t in (c for c in conflicts if c[0] == st):
                print "on", t
                print "\n".join('   ' + str(a) + ' ' + (a == 'R' and R.R[d][0]
                                                                  or str(d))
                                for (a, d) in R.ACTION[s][t])
    return R


cache_is_valid = ((analyzeRcached_grammar == R_grammar)
                  and os.path.isfile(ANALYZERCACHE_PARSER))

if cache_is_valid:
    R = cPickle.load(open(ANALYZERCACHE_PARSER))
    print "Reusing cached parser"
else:
    open(ANALYZERCACHE_GRAMMAR, 'w').write(R_grammar)
    R = init_parser()
    print "Built parser in", R.build_time, 'seconds'
    print "Unused rules :", R.unused_rules
    print len(R.conflicts()), "conflicts."
    cPickle.dump(R, open(ANALYZERCACHE_PARSER, 'w'), 2)


def parse(filename=None, text=None):
    if RContext.current_file[-1] != '':
        print "[sourced by %s]" % RContext.current_file[-1],
    parses = R(filename, text)
    return parses and parses[0]

RContext.parse = staticmethod(parse)
