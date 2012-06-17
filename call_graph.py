from parseR import parse
from entities import *
from itertools import *
import sys
import os


def get_context(r):
    while True:
        if type(r) in (Function, Script):
            return r
        r = r.parent


def get_call_graph(s):
    # find all calls
    calls = list(s.search_iter(lambda x: type(x) is Call))
    # find all function declarations
    func_decls = list(s.search_iter(lambda x: type(x) is Function))
    print "Declared", ', '.join(set(f.name.name for f in func_decls))
    # searchable version of func_decls
    funcs = dict((f.name.name, f) for f in func_decls)
    # filter out calls to functions outside the parsed code
    local_calls = filter(lambda c: c.callee.name in funcs, calls)
    print "Called", ', '.join(set(c.callee.name for c in local_calls))
    # now determine the context of each call
    contextualized_calls = [(get_context(c), c) for c in local_calls]
    called = set(c.callee.name for c in calls)
    never_called = set(c for c in funcs.iterkeys() if c not in called)
    call_graph = list((type(ct) is Function and ct.name.name or "<script>",
                       ct.get_filename(),
                       c.callee.name, funcs[c.callee.name].get_filename())
                      for (ct, c) in contextualized_calls)
    return funcs, call_graph, never_called


def call_graph_to_dot(cg, out=sys.stdout):
    clusters = set(f.get_filename() for f in cg[0].itervalues())
    clusdic = {}
    for c in clusters:
        clusdic[c] = list()
    clus_hash = dict(izip(chain(xrange(len(clusters)), clusters),
                          chain(clusters, xrange(len(clusters)))))
    functions = cg[0].keys() + ['script' + str(i)
                                for i in xrange(len(clusters))]
    func_hash = dict(izip(chain(xrange(len(functions)), functions),
                          chain(functions, xrange(len(functions)))))
    for fd in cg[0].itervalues():
        clusdic[fd.get_filename()].append(fd.name.name)
    #print "clusters", clusters
    #print "clusdic", clusdic
    #print "clus_hash", clus_hash
    print >> out, "digraph call_graph {"
    print >> out, '  title="Call graph"'
    print >> out, '  aspect=1;'
    node_linked = dict(izip_longest(func_hash.iterkeys(), [], fillvalue=False))
    for (caller, caller_file, callee, callee_file) in cg[1]:
        if caller == '<script>':
            n0 = 'script%i' % clus_hash[caller_file]
        else:
            n0 = caller
        n1 = callee
        node_linked[n0] = True
        node_linked[n1] = True
    for c in clusdic:
        print >> out, "  subgraph cluster%i {" % clus_hash[c]
        print >> out, '    label="%s";' % c
        scriptn = 'script%i' % clus_hash[c]
        if node_linked[scriptn]:
            print >> out, '    %i [label="<script>"];' % func_hash[scriptn]
        for k in clusdic[c]:
            if node_linked[k]:
                print >> out, '    %i [label="%s"];' % (func_hash[k], k)
        print >> out, "  }"
    for (caller, caller_file, callee, callee_file) in set(cg[1]):
        if caller == '<script>':
            n0 = func_hash['script%i' % clus_hash[caller_file]]
        else:
            n0 = func_hash[caller]
        n1 = func_hash[callee]
        print >> out, "  %i -> %i;" % (n0, n1)
    print >> out, "}"


def make_call_graph(filename):
    dotfile = filename + '.dot'
    output = filename + '.png'
    call_graph_to_dot(get_call_graph(parse(filename)), open(dotfile, 'w'))
    os.system('dot -Tpng -o %s %s' % (output, dotfile))
    print "Output global call graph as", output
#
