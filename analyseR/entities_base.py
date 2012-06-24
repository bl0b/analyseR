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

class Path(object):

    def __init__(self, ev=None, it=None, pr=None, **kw):
        if not kw:
            self.x = {'e': ev, 'i': it, 'p': pr}
        else:
            check = lambda e, k, v: hasattr(e, k) and v(getattr(e, k))
            self.x = {'e': lambda e: e,
                      'i': lambda e: (e,),
                      'p': lambda e: reduce(lambda a, b: a and check(e, *b),
                                            kw.iteritems(),
                                            True)}

    def search(self, ent):
        return (self.x['e'](x)
                for x in self.x['i'](ent)
                if self.x['p'](x))

    def __div__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for x in pa.search(ent)
                                 for r in x.children()),
                    pb.x['p'])

    def __floordiv__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for x in pa.search(ent)
                                 for r in x.deep()),
                    pb.x['p'])

    def __getattr__(pa, attr):
        return Path(lambda ent: getattr(pa.x['e'](ent), attr),
                    pa.x['i'],
                    lambda ent: pa.x['p'](ent) and hasattr(ent, attr))

    def __getitem__(pa, idx):
        return Path(lambda ent: ent[idx],
                    pa.x['i'],
                    lambda ent: pa.x['p'](ent) and hasattr(ent, '__getitem__'))

    def __sub__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: ent.before(),
                    pb.x['p'])

    def __neg__(pa):
        return Path(pa.x['e'],
                    pa.x['i'],
                    lambda ent: not pa.x['p'](ent))


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

    def children(self):
        return iter(self)

    def deep(self):
        return (x
                for c in self
                for x in c.search_iter(lambda x: True)
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
            return Path(**kw)
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

    def children(self):
        return (x
                for e in self.entrails
                for ent in (getattr(self, e),)
                for x in (isinstance(ent, Rentity) and (ent,) or ent))

    def deep(self):
        return (self.search_iter(lambda x: True))

    def before(self):
        p = self.previous
        while p:
            yield p
            p = p.previous

    def above(self):
        p = self.parent
        while p:
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
            return self.names[name][-1]
        return None

    def __iter__(self):
        return (getattr(self, x) for x in self.entrails)

    def __div__(self, what):
        return [x for c in self.children() for x in what.search(c)]

    def __floordiv__(self, what):
        return [x for c in self.deep() for x in what.search(c)]

    def __sub__(self, what):
        return [x for c in self.before() for x in what.search(c)]


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
