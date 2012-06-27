from parseR import parse
from entities import *
from itertools import *
import sys
import os


def find_func_parent(e):
    p = e.get_path()
    for x in reversed(p):
        if type(x) is Function:
            # return assigned name if it exists, file:line otherwise
            if type(x.parent) is Assign:
                return x.parent.lhs.name
            return x.name
    return 'script:' + p[0].get_filename()


def pp(x):
    if type(x) is Call and type(x.callee) is Name and x.callee.name == 'paste':
        # special case : we keep strings and sep argument,
        # and everything else is *.
        ret = []
        sep = " "  # R's default value
        for p in x.params.expressions:
            if type(p) is Assign and p.lhs.name == 'sep':
                sep = p.rhs.eval_to().value()
        for p in x.params.expressions:
            if type(p) is Assign and p.lhs.name == 'sep':
                continue
            if type(p) is Immed:
                ret.append(p.value())
            else:
                ret.append('*')
        return sep.join(ret)

    else:
        return x.pp()


def find_calls_by_name(s, start):
    clist = list(s // Call(callee=lambda x: type(x) is Name
                                            and x.name.startswith(start)
                                            and x.eval_to() is x))
    return [(find_func_parent(c), c) for c in clist]


def process_read(r):
    fname = reduce(lambda a, b: type(b) is Assign
                                and type(b.lhs) is Name
                                and b.lhs.name == 'file'
                                and b
                                or a,
                                r.params.expressions)
    return (r.callee.name,
           pp((type(fname) is Assign and fname.rhs or fname).eval_to()))


def process_write(w):
    print w
    fname = reduce(lambda a, b: type(b) is Assign
                                and type(b.lhs) is Name
                                and b.lhs.name == 'file'
                                and b.rhs
                                or a,
                                w.params.expressions[1:])
    return (w.callee.name, w.params.expressions[0].pp(),
            pp((type(fname) is Assign and fname.rhs or fname).eval_to()))


def process_reads(s):
    return map(lambda (p, r): (p,) + process_read(r),
               find_calls_by_name(s, "read."))


def process_writes(s):
    return map(lambda (p, w): (p,) + process_write(w),
               find_calls_by_name(s, "write."))


def process_call(c):
    return c.callee.eval_to()


def process_calls(s):
    return map(lambda c: (find_func_parent(c), process_call(c)), s // Call)


def io_nodes(s):
    return {'reads': process_reads(s), 'writes': process_writes(s)}


def io_graph(s):
    reads = process_reads(s)
    writes = process_writes(s)

    import pygraphviz as pgv
    g = pgv.AGraph(directed=True)
    for whence, how, from_ in reads:
        g.add_node(str(whence), label=str(whence), shape="rectangle")
        g.add_node(str(from_), label=str(from_), shape="ellipse")
        g.add_edge(str(from_), str(whence), label=str(how))
    for whence, how, what, into in writes:
        g.add_node(str(whence), label=str(whence), shape="rectangle")
        g.add_node(str(into), label=str(into), shape="ellipse")
        g.add_edge(str(whence), str(into), label=str(how) + '('
                                                 + str(what) + ')')
    return g



#writes = [(a.rhs, a.get_filename()) for w in (s // (Call(callee=lambda x:
#type(x) is Name and x.name.startswith('write.')))) for a in
#(w//Assign(lhs=lambda x: x.name=='file'))]


def toplevel_calls(e):
    return list(s // Call(parent=lambda x: x is not None
                                             and not list(x ** Function)))


cond_num = 0


def make_cond_name():
    global cond_num
    cond_num += 1
    return '..cond.expr.' + str(cond_num)


def expand_ifelse(ifelse):
    cond = make_cond_name()
    sta = [None, Assign((None, Name(cond), ('LEFT_ARROW',), ifelse.condition))]
    if isinstance(ifelse.then, Statements):
        sta += [IfElse(None, Name(cond),
                       x, None)
                for x in ifelse.then.statements]
    else:
        sta += [IfElse(None, Name(cond),
                       ifelse.then, None)]
    if isinstance(ifelse.els_, Statements):
        sta += [IfElse(None, Negation((None, None, Name(cond))),
                       x, None)
                for x in ifelse.els_.statements]
    elif ifelse.els_:
        sta += [IfElse(None, Negation((None, None, Name(cond))),
                       ifelse.els_, None)]
    print sta
    return Bloc(sta)


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
