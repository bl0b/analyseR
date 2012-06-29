from analyseR import *
from analyseR.entities_base import shield


def section(*s):
    print "#" * 80
    print '#', '\n#'.join(s)
    print "#" * 80

section('parsing')
s = parse('MAIN.R')
section("checking")
check(s)
section('shielding')
shield(s // Any)
section('run all_nodes')
n = all_nodes(s)
section('create io+call graph')
g = io_and_call_graph(n)
section('checking')
check(s)
section('output dot script into io_and_call.dot')
print >> open('io_and_call.dot', 'w'), g.to_string()
section('removing io')
n['reads'] = []
n['writes'] = []
n['nr'] = set()
n['nw'] = set()
section('writing pure call graph')
g = io_and_call_graph(n)
print >> open('call_graph.dot', 'w'), g.to_string()
