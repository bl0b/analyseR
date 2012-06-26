import os
import sys


def strip_common_path(*ents):
    i = -1
    paths = zip(*[e.get_path() for e in ents])
    for p in paths:
        if reduce(lambda a, b: a is b and a or None, p) is not None:
            i += 1
        else:
            break
    return paths[i][0]


def find_closest_common_parent(patha, pathb):
    return reduce(lambda a, (pa, pb): pa == pb and pa or a,
                  izip(patha, pathb))


#_entrail_get = lambda e: lambda self: getattr(self, '_' + e)


class NotWanted(Exception):
    pass


class Path(object):

#    def __init__(self, ev=None, it=None, pr=lambda e: True, **kw):
#        if not kw:
#            self.x = {'e': ev, 'i': it, 'p': pr}
#        else:
#            check = lambda e, k, v: hasattr(e, k) and v(getattr(e, k))
#            self.x = {'e': lambda e: e,
#                      'i': lambda e: (e,),
#                      'p': lambda e: reduce(lambda a, b: a and check(e, *b),
#                                            kw.iteritems(),
#                                            True)}

    def __init__(self, ev, it, pr=lambda e: True):
        self.x = {'e': ev, 'i': it, 'p': pr}

    def __call__(self, **kw):
        check = lambda e, k, v: hasattr(e, k) and v(getattr(e, k))
        pred = lambda e: (self.x['p'](e)
                          and reduce(lambda a, b: a and check(e, *b),
                                     kw.iteritems(),
                                     True))
        return Path(self.x['e'], self.x['i'], pred)

    def search(self, ent):
        i = self.x['i']
        e = self.x['e']
        p = self.x['p']
        try:
            for x in i(ent):
                if p(x):
                    yield e(x)
        except NotWanted:
            pass
        #return (e(x) for x in i(ent) if p(x))

    def __getattr__(pa, attr):
        return Path(lambda ent: getattr(pa.x['e'](ent), attr),
                    pa.x['i'],
                    lambda ent: pa.x['p'](ent) and hasattr(ent, attr))

    def __getitem__(pa, idx):
        return Path(lambda ent: pa.x['e'](ent)[idx],
                    pa.x['i'],
                    lambda ent: pa.x['p'](ent) and hasattr(ent, '__getitem__'))

    def __or__(pa, pb):
        return Path(lambda ent: pa.x['p'](ent)
                                and pa.x['e'](ent)
                                or pb.x['e'](ent),
                    lambda ent: chain(pa.x['i'](ent), pb.x['i'](ent)),
                                # this chaining may be awful.
                    lambda ent: pa.x['p'](ent) or pb.x['p'](ent))

    def __div__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for x in pa.search(ent)
                                 for r in x.children(pb.x['p'])))

    def __floordiv__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for x in pa.search(ent)
                                 for r in x.deep(pb.x['p'])))

    def __sub__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: ent.before(pb.x['p']))

    def __mul__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: ent.parent and pb.x['p'](ent.parent)
                                and (ent.parent,)
                                or tuple())

    def __pow__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: ent.above(pb.x['p']))

    def __rdiv__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: pa.children(pb.x['p'])).search(pa)

    def __rfloordiv__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for r in pa.deep(pb.x['p']))).search(pa)

    def __rsub__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: ent.before(pb.x['p'])).search(pa)

    def __rmul__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: ent.parent and pb.x['p'](ent.parent)
                                and (ent.parent,)
                                or tuple()).search(pa)

    def __rpow__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: ent.above(pb.x['p'])).search(pa)

    def __neg__(pa):
        p = pa.x['p']

        def _p(ent):
            if p(ent):
                raise NotWanted()
            return True
        return Path(pa.x['e'],
                    pa.x['i'],
                    _p)


def _entrail_get(e):
    ename = e
    e = '_' + e

    def _(self):
        x = getattr(self, e)
#        if isinstance(x, tuple):
#            return RProxyTuple(ename, x)
#        elif isinstance(x, list):
#            return RProxyList(ename, x)
        return x

    return _


def _entrail_set(e):
    e = '_' + e

    def _(self, v):
        if type(v) in (list, tuple):
            for x in v:
                if isinstance(x, Rentity):
                    x.set_parent(self)
        elif isinstance(v, Rentity):
            v.set_parent(self)
        setattr(self, e, v)
        #print "set entrail", e, v, getattr(self, '_' + e)
        return v

    return _


class Rentrail(property, Path):

    def __init__(self, cls, name):
        property.__init__(self, _entrail_get(name), _entrail_set(name))
        Path.__init__(self,
                      lambda ent: getattr(ent, name),
                      lambda ent: (ent,),
                      lambda ent: isinstance(ent, cls) and hasattr(ent, name))
        #self.owner = None
        self.name = name
        self.cls = cls

    #def before(self):
    #    p = self.owner.previous
    #    while p:
    #        yield p
    #        p = p.previous

    #def above(self):
    #    p = self.owner.parent
    #    while p:
    #        yield p
    #        p = p.parent

    def children(self, pred):
        return (x for x in self if pred(x))

    def deep(self, pred):
        return (x
                for c in self
                for x in c.search_iter(pred)
                if isinstance(c, Rentity))

    def _expr(self, x):
        return getattr(x, self.name)

    def _validate(self, x):
        return type(x) is self.cls


___indent = 0


def call_dumper(cls, name):
    m = getattr(cls, name)

    def _ret(*a, **kw):
        global ___indent
        print >> sys.stderr, "%sCalling %s.%s" % (' ' * ___indent,
                                                  cls.__name__, name), a, kw
        ___indent += 2
        ret = m(*a, **kw)
        ___indent -= 2
        print >> sys.stderr, "%s=>" % (' ' * ___indent), ret
        return ret
    return _ret


class RentityMeta(type, Path):
    registry = {}

    def __init__(cls, name, bases, dic):
        Path.__init__(cls,
                      lambda e: e,
                      lambda e: (e,),
                      lambda e: isinstance(e, cls))
        RentityMeta.registry[name.lower()] = cls
        for e in cls.entrails:
            setattr(cls, e, Rentrail(cls, e))
        #setattr(cls, 'eval_to', call_dumper(cls, "eval_to"))
        #setattr(cls, 'resolve', call_dumper(cls, "resolve"))

    def _expr(self, x):
        return x

    def _validate(self, x):
        return type(x) is self


class Rentity(object):
    __metaclass__ = RentityMeta
    entrails = []

    def __new__(cls, *a, **kw):
        if kw and not a:
            return Path.__call__(cls, **kw)
        return object.__new__(cls)

    def __init__(self):
        for e in self.entrails:
            setattr(self, '_' + e, None)
            #getattr(self, e).owner = self
        self.filename = RContext.current_file[-1]
        self.parent = None
        self.previous = None
        #for e in self.entrails:
        #    setattr(self, e, None)

    def set_parent(self, p):
        self.parent = p

    def eval_name(self, n):
        return None

    def __repr__(self):
        if type(self).__str__ is object.__str__:
            return object.__repr__(self)
        return str(self)

    def search_iter(self, predicate, forbid=[]):
        if type(self) in forbid:
            return
        if predicate(self):
            yield self
        for e in self.entrails:
            x = getattr(self, e)
            if type(x) in (list, tuple):
                for k in x:
                    if not isinstance(k, Rentity):
                        if predicate(k):
                            yield k
                        continue
                    for result in k.search_iter(predicate, forbid):
                        yield result
            elif isinstance(x, Rentity):
                for result in x.search_iter(predicate, forbid):
                    yield result

    def children(self, pred):
        return (x
                for e in self.entrails
                for ent in (getattr(self, e),)
                for x in (isinstance(ent, Rentity) and (ent,) or ent)
                if pred(x))

    def deep(self, pred):
        return (self.search_iter(pred))

    def before(self, pred):
        p = self.previous
        while p:
            if pred(p):
                yield p
            p = p.previous

    def above(self, pred):
        p = self.parent
        while p:
            if pred(p):
                yield p
            p = p.parent

    def get_filename(self):
        if hasattr(self, 'filename'):
            return self.filename
        elif self.parent:
            return self.parent.get_filename()

    def eval_to(self):
        return self

    def reg_name(self, name, value):
        if self.parent:
            self.parent.reg_name(name, value)

    def get_path(self):
        if self.parent:
            return self.parent.get_path() + [self]
        else:
            return [self]

    def resolve(self, name):
        if type(name) is Name:
            if name.visibility is not None:
                return name
            name = name.name
        if hasattr(self, "names") and name in self.names:
            #print self, "has names and has", name, self.names[name]
            return self.names[name][-1].eval_to()
        return None

    def __iter__(self):
        return (getattr(self, x) for x in self.entrails)

#    def __div__(self, what):
#        return [x
#                for c in self.children(lambda x: True)
#                for x in what.search(c)]

#    def __floordiv__(self, what):
#        return [x for c in self.deep(lambda x: True) for x in what.search(c)]

#    def __sub__(self, what):
#        return [x
#                for c in self.before(lambda x: True)
#                for x in what.search(c)]

#    def __mul__(self, what):
#        return self.parent and [x for x in what.search(self.parent)] or []

#    def __pow__(self, what):
#        return [x for p in self.above(lambda x: True) for x in what.search(p)]


Any = Path(lambda e: e, lambda e: (e,), lambda e: True)


class RProxy(Rentity):

    def __init__(self, name):
        Rentity.__init__(self)
        self._name = name


class RProxyList(list, RProxy):

    def __init__(self, name, l):
        list.__init__(self, l)
        RProxy.__init__(self, name)


class RProxyTuple(tuple, RProxy):

    def __new__(cls, name, t):
        return tuple.__new__(cls, t)

    def __init__(self, name, t):
        tuple.__init__(self)
        RProxy.__init__(self, name)


class Renv(object):

    def __init__(self):
        self.names = {}

    def reg_name(self, name, value):
        if name in self.names:
            self.names[name].append(value)
        else:
            self.names[name] = [value]

    def resolve(self, name):
        #print "resolution of", name, "in", self.names
        if name in self.names:
            return self.names[name][-1]
        return None


class RContext(object):
    current_file = ['']             # implementing reentrant parses
    current_text = ['']             # //   //         //      //
    current_dir = [os.getcwd()]     # //   //         //      //
    parse = None                    # shameful hack to prevent hard
                                    # circular dependency.
    call_resolution = []            # implementing call stack


class Statement(Rentity):

    def __init__(self):
        Rentity.__init__(self)


class AllIndices(Rentity):

    def __str__(self):
        return "AllIndices"


allindices = AllIndices()


def wrap_previous(get_target):

    def _set(s, v):
        try:
            t = get_target(s)
            if t is not None:
                t.previous = v
        except:
            pass

    def _get(s):
        try:
            t = get_target(s)
            return t and t.previous
        except:
            return None

    return property(_get, _set)


def extract_list(ast):
    ret = []
    on_comma = True
    #print "extract_list", ast
    for a in ast:
        #print "extract_list on", a
        if type(a) is tuple:
            if a[0] == 'COMMA':
                if on_comma:
                    ret.append(allindices)
                else:
                    on_comma = True
            #else:
            #    print "extract_list on tuple", a
        else:
            on_comma = False
            ret.append(a)
    return ret


def chain_ifelse(ifelse, smthg):
    ret = ifelse
    while type(ifelse) is IfElse and ifelse.els_:
        ifelse = ifelse.els_
    if type(ifelse) is IfElse:
        ifelse.els_ = smthg
    return ret


class Name(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self)
        if isinstance(ast, str):
            self.name = ast
            self.visibility = None
            self.namespace = None
        elif len(ast) == 4:
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

    def eval_to(self):
        pathass = Assign(lhs=lambda x: type(x) is Name and x == self)
        # discard None's
        defs = filter(lambda x: x is not None,
                      (x.resolve(self)
                       for x in self - (pathass | If // pathass)))
        # retain all IfElse's and only one previous eval (possible final else).
        defs = reduce(lambda accum, d:
                      accum[0] and (type(d) is IfElse, accum[1] + [d])
                                or accum,
                      defs,
                      (True, []))[1]
        # now chain if's as much as can do
        #print "defs", defs
        if len(defs) > 1:
            #print "tmp", reduce(chain_ifelse, defs)
            #return strip_common_path(*defs)
            return reduce(chain_ifelse, defs)
        if len(defs) == 0 or defs[0] is None:
            return self
        return defs[0]

    def resolve(self, n):
        if self is n:
            return self
        return None

    def __eq__(self, a):
        if type(a) is type(self):
            return (self.namespace == a.namespace and self.name == a.name)
        else:
            return False

    def __hash__(self):
        return hash(self.namespace) + hash(self.name)


class Assign(Statement):
    entrails = ['lhs', 'rhs']

    def __set_previous(s, p):
        if s.lhs:
            s.lhs.previous = p
        if s.rhs:
            s.rhs.previous = p

    def __get_previous(s):
        return s.lhs and s.lhs.previous or None

    previous = property(__get_previous, __set_previous)

#    def __new__(self, ast, rightwards=False):
#        if rightwards:
#            n, f = 3, 1
#        else:
#            n, f = 1, 3
#        #if type(ast[n]) is Name and type(ast[f]) is Function:
#        #    return ast[f].make_name(ast[n])
#        return Rentity.__new__(Assign)

    def __init__(self, ast, rightwards=False):
        Statement.__init__(self)
        if rightwards:
            self.lhs = ast[3]
            self.rhs = ast[1]
        else:
            self.lhs = ast[1]
            self.rhs = ast[3]
        self.assign = ast[2][0]

    def __str__(self):
        return 'Assign(lhs=' + str(self.lhs) + ', rhs=' + str(self.rhs) + ')'

    def eval_to(self):
        return self.rhs.eval_to()

    def set_parent(self, p):
        Statement.set_parent(self, p)
        self.reg_name(self.lhs, self.rhs)

    def resolve(self, name):
        if self.lhs == name:
            return self.rhs
        return None


class If(Statement):
    entrails = ['condition', 'then', 'els_']

    def __get_previous(self):
        return self.condition and self.condition.previous

    def __set_previous(self, p):
        if self.condition:
            self.condition.previous = p

    previous = property(__get_previous, __set_previous)

    def __init__(self, ast):
        Statement.__init__(self)
        #print "IF (ast)", ast
        self.condition = ast[3]
        self.then = ast[5]
        if self.then == None:
            raise Exception('IF ' + str(ast) + ' '
                            + str(ast[3]) + ' '
                            + str(ast[5]) + ' '
                            + str(ast[7]))
        self.els_ = len(ast) == 8 and ast[7] or None
        if self.then:
            self.then.previous = self.condition
        if self.els_:
            self.els_.previous = self.condition
        #print "IF (properties)", self.condition, self.then, self.els_

    def __str__(self):
        ret = type(self).__name__
        ret += '(condition=' + str(self.condition)
        ret += ', then=' + str(self.then)
        if self.els_ is not None:
            ret += ', else=' + str(self.els_)
        ret += ')'
        return ret

    def resolve(self, n):
        cond = self.condition.eval_to()
        #print "[resolve] If eval cond to", cond
        if isinstance(cond, Immed):
            if cond.value():
                return self.then.resolve(n)
            elif self.els_:
                return self.els_.resolve(n)
        else:
            then = self.then and self.then.resolve(n)
            els_ = self.els_ and self.els_.resolve(n)
            if then is None:
                if els_ is None:
                    return None
                elif isinstance(cond, Negation):
                    return IfElse(self.previous, cond.expression, els_, None)
                else:
                    return IfElse(self.previous, Negation(cond), els_, None)
            return IfElse(self.previous, cond, then, els_)

    def eval_to(self):
        cond = self.condition.eval_to()
        #print "[eval_to] If eval cond to", cond
        if isinstance(cond, Immed):
            if cond.value():
                return self.then.eval_to()
            elif self.els_:
                return self.els_.eval_to()
        else:
            return IfElse(self.previous, cond, self.then.eval_to(),
                          self.els_ and self.els_.eval_to())


class IfElse(If):

    def __init__(self, prev, cond, then, els_):
        #print "IfElse", prev, cond, then, els_
        if isinstance(cond, bool):
            raise Exception()
        If.__init__(self, (None, None, None, cond,
                           None, then, None, els_))
        self.previous = prev


class Immed(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self)
        if (isinstance(ast, int)
                or isinstance(ast, float)
                or isinstance(ast, long)):
            self.typ = 'NUM'
            self.val = str(ast)
        elif isinstance(ast, str):
            self.typ = 'STRING'
            self.val = ast
        else:
            self.typ = ast[1][0]
            self.val = ast[1][1]

    def __str__(self):
        return str(self.typ) + '(' + str(self.val) + ')'

    def value(self):
        if self.typ == "STRING":
            return self.val
        elif self.typ == "NUM":
            return float(self.val)
